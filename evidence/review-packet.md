# Review packet #3244
head: 622be7c53b760156e2453dacbd1724325212b9e4
base: dc0a170b671814be196a54b1c71e29449f54d6d7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127803769186 neutral
arch-score / arch-score id=127803428202 success
arm id=127803228879 skipped
budget-raise-gate / budget-raise-gate id=127803428421 success
cancel-superseded id=127803233902 success
codeql id=127803393003 skipped
codeql / Analyze (actions) id=127803428306 success
codeql / Analyze (javascript-typescript) id=127803428298 success
codeql / Analyze (python) id=127803428254 in_progress
gate id=127803877243 failure
governance id=127803393555 skipped
governance / delivery-status id=127803428269 success
governance / delivery-status-publish id=127803430206 skipped
governance / env-matrix id=127803428307 in_progress
governance / instrument-self-tests id=127803428238 in_progress
governance / policy-docs id=127803428191 in_progress
governance / record id=127803429702 skipped
governance / wave-script id=127803428361 success
hassfest id=127803393898 skipped
hassfest / hassfest id=127803428128 success
kernel-points id=127803429237 skipped
pr-contract id=127803879674 skipped
prelude id=127803234366 success
refresh id=127803234347 success
tests id=127803393068 skipped
tests / arch-instrument id=127803647657 success
tests / briefs id=127803428143 success
tests / browser id=127803647715 in_progress
tests / closure-scope id=127803428227 success
tests / closures id=127803647740 in_progress
tests / coverage id=127803647738 in_progress
tests / fast (3.14) id=127803647665 in_progress
tests / mutation id=127803428129 success
tests / mutation-autofix id=127803739174 skipped
tests / mutation-pins id=127803737942 skipped
tests / nightly-ha id=127803649693 skipped
tests / nightly-status id=127803428208 success
tests / replay id=127803649888 skipped
tests / typing id=127803647724 success
validate id=127803392661 skipped
validate / validate-hacs id=127803427945 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at 622be7c53b760156e2453dacbd1724325212b9e4

## Advisories
none

## carry_audit at the head
NOTE body item 83ea0456: dismissed:owner ruling territory, stated for the owner in the docs and this body
NOTE body item 8fbe1d1c: dismissed:a session plugin outside this repository's policy
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py wood-plant
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         python3 tests/plan_view.py
             `tests/plan_view.py` is in the tree at this head
  ok         PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs
             `tests/card_browser.mjs` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git diff --quiet origin/main -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 7 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index c4b8dfb48..c25a5369e 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -9922,7 +9922,7 @@ const RECEIPT_CSS = `
 const finiteNum = (n) => typeof n === "number" && Number.isFinite(n);
 
 /** The latest receipt's lines, its total and where its spot money went. */
-function receiptHtml(st, rows, cur) {
+function receiptHtml(st, rows, cur, wood) {
   const list = Array.isArray(st.attributes.receipts) ? st.attributes.receipts : [];
   const r = list.length ? list[list.length - 1] : null;
   if (!r || !r.lines || typeof r.lines !== "object") return "";
@@ -9948,7 +9948,9 @@ function receiptHtml(st, rows, cur) {
     ? `<div>${esc(L("receipt.saved", {
         amount: row.savings_sek.toFixed(2), unit: cur,
         pct: finiteNum(row.savings_pct) ? `${row.savings_pct.toFixed(0)} %` : "—",
-      }))}</div>`
+      }))}</div>${wood
+        ? `<div class="receipt-sub receipt-wood-note">${esc(L("savings.wood_note"))}</div>`
+        : ""}`
     : "";
   const covers = basis.map((n) => L(`receipt.line_${n}`).toLowerCase()).join(", ");
   const reasons = Object.entries(r.reasons || {})
@@ -14925,7 +14927,12 @@ class HeatpumpOptimizerCard extends HTMLElement {
     const cur = savingsUnit(this.plan, "_plan_monthly_savings");
     // R9-UX-6: the closed month's receipt and yesterday's replay come first;
     // the table of every month below them is unchanged.
-    const drawn = `${receiptHtml(st, rows, cur)}${replayHtml(st, cur)}`;
+    // The reference has no wood: on a house with wood configured every saving
+    // the page states, the receipt's and the table's, says so (owner ruling,
+    // 2026-11-04).
+    const fuel = this.plan.woodFuel();
+    const wood = !!(fuel && fuel.show_whatif);
+    const drawn = `${receiptHtml(st, rows, cur, wood)}${replayHtml(st, cur)}`;
     const top = drawn ? `<style>${RECEIPT_CSS}</style>${drawn}` : "";
     const money = (n) => (finiteNum(n) ? n.toFixed(2) : "—");
     const pct = (n) => (finiteNum(n) ? `${n.toFixed(0)}%` : "—");
@@ -14959,8 +14966,7 @@ class HeatpumpOptimizerCard extends HTMLElement {
     // the same unit down the whole column, and repeating it is what pushed
     // the decimal points out of line.
     const head = (key) => `${esc(L(key))} (${esc(cur)})`;
-    const fuel = this.plan.woodFuel();
-    const woodNote = fuel && fuel.show_whatif
+    const woodNote = wood
       ? `<div class="savings-wood-note" style="margin-top:.6em;font-size:.9em;color:var(--secondary-text-color)">${esc(L("savings.wood_note"))}</div>`
       : "";
     return `${top}<table class="savings-table">
diff --git a/dev/audit/harnesses/r10_sav_wood_reference.py b/dev/audit/harnesses/r10_sav_wood_reference.py
index 19b3c6cef..764134aff 100644
--- a/dev/audit/harnesses/r10_sav_wood_reference.py
+++ b/dev/audit/harnesses/r10_sav_wood_reference.py
@@ -26,6 +26,23 @@ so a positive row on these arms is wood's heat, expected, and the card says so:
 firewood's cost is not counted. ``wood-unforeseen`` meters under the plan: with
 wood configured the row's calibration only raises the reference (floor 1.0), and
 the arm prints what the uncalibrated row reads beside it.
+Its meter is a stated multiplier, not the plant's: it measures the floor's
+arithmetic, not the size of the heat.
+
+``wood-plant`` measures that size (R10-SAV-WOOD-HEAT). The fire is in the plant
+only (``FIRE_KW`` x ``FIRE_START_H``, ``FIRE_HOURS`` long, never forecast); the
+plant pump tracks the plan's own buffer trajectory over each ``REPLAN`` hold, so
+it draws less once wood carries the draw, and the meter reads
+``METER_OVER_MODEL`` m times what it drew (m: the model's own meter error,
+which the calibration exists to correct). The figure is the applied
+calibration's error against the true m, the fire's share being that error less
+the no-fire run's: ``RESULT wood_plant_error_m<m>`` with its spread over the
+grid. Controls: no fire, and flat prices (the row is volume only); the
+perturbation is the largest fire with the pump blind to it (meter = plan),
+whose error from the heat must read zero. What it cannot show: a real pump's
+control loop, a fire's coupling on a real house, or the coordinator's
+per-interval re-plan (the hold is ``REPLAN`` intervals, a wider window for the
+meter to leave the plan than production's one).
 
     PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py [--quick] [--no-settlement] [arm ...]
 """
@@ -211,6 +228,140 @@ def valve_arm(price: str) -> bool:
     return price != "flat" or abs(row["savings_pct"]) < FLAT_BAND_PCT
 
 
+#: The plant arm's grid: fire size kW, start hour, a 4 h burn; and the plant
+#: pump's metered kWh per kWh the model books (the model's own meter error).
+FIRE_KW = (4.0, 8.0, 12.0)
+FIRE_START_H = (6, 17, 22)
+FIRE_HOURS = 4
+METER_OVER_MODEL = (0.8, 1.0, 1.2)
+
+
+def _pump_response(model, state, plan_kw, args, fire_kw, target):
+    """The plant pump's kW: the plan's, cut so the buffer ends no warmer than ``target``.
+
+    Actuation is a setpoint, not a power: the pump stops charging once the
+    buffer reaches the plan's own trajectory at the step's end, which the
+    plan solved without the fire. Bisection on the plant's own step.
+    """
+    def end(p):
+        return model.simulate_step(state, p, *args, external_heat_kw=fire_kw).buffer_tank_temperature
+    if plan_kw <= 0.0 or end(plan_kw) <= target + 1e-9:
+        return plan_kw
+    if end(0.0) >= target:
+        return 0.0
+    lo, hi = 0.0, plan_kw
+    for _ in range(30):
+        mid = 0.5 * (lo + hi)
+        lo, hi = (mid, hi) if end(mid) <= target else (lo, mid)
+    return lo
+
+
+def plant_loop(burn_kw, price: str, respond: bool = True, foresee: bool = False, wood0: float = 40.0):
+    """wood-plant: the fire is in the plant and not the plan; the meter is the pump's response.
+
+    Returns, per ``METER_OVER_MODEL`` m, the row the ledger books and the
+    applied calibration, plus the plant's metered and planned kWh. The plan
+    books ``power``; the plant pump draws ``_pump_response`` (``respond``
+    False: the plan's power, the perturbation that leaves the meter blind to
+    the fire); the meter reads m times what it drew.
+    """
+    opt, model = _install(True)
+    total, hs = int(DAYS * 24 / DT), int(24 / DT)
+    span = total + hs + 4
+
+    def tile(a):
+        a = np.asarray(a, dtype=float)
+        return np.tile(a, int(np.ceil(span / len(a))))[:span]
+
+    pr = tile(prices(price, START))
+    out, wind, rain, sol = (tile(a) for a in weather("winter_cold", START))
+    ext = np.array([burn_kw(START + timedelta(hours=k * DT)) for k in range(span)], float)
+    state = ThermalState(
+        room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=float(out[0]),
+        upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+        buffer_tank_temperature=30.0, wood_tank_temperature=wood0,
+    )
+    leds = {m: MonthlyLedger() for m in METER_OVER_MODEL}
+    plan_kwh = drawn_kwh = fire_kwh = 0.0
+    plan = None
+    for k in range(total):
+        now = START + timedelta(hours=k * DT)
+        forecast = ext[k:k + hs].copy()
+        forecast[int(2.0 / DT):] = 0.0
+        if not foresee:
+            forecast[:] = 0.0
+        series = WeatherSeries(
+            outdoor_temps=out[k:k + hs], wind_speeds=wind[k:k + hs], precipitation=rain[k:k + hs],
+            solar_radiation=sol[k:k + hs], external_heat_kw=forecast,
+        )
+        if k % REPLAN == 0:
+            plan = opt.optimize(inputs=solve_inputs(
+                initial_state=state, prices=pr[k:k + hs], outdoor_temps=out[k:k + hs],
+                wind_speeds=wind[k:k + hs], precipitation=rain[k:k + hs],
+                solar_radiation=sol[k:k + hs], start_time=now, external_heat_kw=forecast,
+            ))
+        power = float(plan.power_schedule[k % REPLAN])
+        args = (float(out[k]), float(wind[k]), float(rain[k]), float(sol[k]), DT)
+        # The plan's buffer at this step's end, solved at its replan: a burn
+        # since then is heat the target does not know of.
+        target = float(plan.buffer_temp_trajectory[k % REPLAN + 1])
+        drawn = _pump_response(model, state, power, args, float(ext[k]), target) if respond else power
+        booked = float(opt._compute_baseline_power(series, state, DT)[0][0])
+        step = {} if NO_SETTLEMENT else dict(_settlement_at(plan, k % REPLAN))
+        for m, led in leds.items():
+            meter = drawn * DT * m
+            led.observe_spot_and_settle_savings(
+                now, float(pr[k]), {**step, "baseline_kw": booked, "power": power}, meter, DT
+            )
+            led.add(now, "spot", kwh=meter, sek=meter * float(pr[k]))
+        plan_kwh += power * DT
+        drawn_kwh += drawn * DT
+        fire_kwh += float(ext[k]) * DT
+        state = model.simulate_step(state, drawn, *args, external_heat_kw=float(ext[k]))
+    rows = {m: led.savings_months(datetime(2026, 2, 1), wood_configured=True)[0] for m, led in leds.items()}
+    return rows, plan_kwh, drawn_kwh, fire_kwh
+
+
+def _booking_error_pct(row, m) -> float:
+    """The booked baseline against the one calibrated by the model's true meter error m, percent.
+
+    Every term of ``baseline_sek`` scales with the applied calibration, so the
+    oracle baseline is ``baseline_sek * m / applied``.
+    """
+    return (row["meter_calibration"] / m - 1.0) * 100.0
+
+
+def wood_plant() -> None:
+    price = "winter_typical"
+    base_rows, base_plan, base_drawn, _ = plant_loop(lambda t: 0.0, price)
+    flat_rows, *_ = plant_loop(lambda t: 0.0, "flat")
+    print(f"  no fire ({price}): plan {base_plan:.2f} kWh, drawn {base_drawn:.2f} kWh")
+    for m in METER_OVER_MODEL:
+        print(f"    m {m}: pct {base_rows[m]['savings_pct']} calibration {base_rows[m]['meter_calibration']}"
+              f" error {_booking_error_pct(base_rows[m], m):+.2f} %; flat pct {flat_rows[m]['savings_pct']}")
+    errs = {m: [] for m in METER_OVER_MODEL}
+    for kw in FIRE_KW:
+        for h0 in FIRE_START_H:
+            burn = (lambda kw, h0: lambda t: kw if (t.hour - h0) % 24 < FIRE_HOURS else 0.0)(kw, h0)
+            rows, plan_kwh, drawn_kwh, fire_kwh = plant_loop(burn, price)
+            for m in METER_OVER_MODEL:
+                # The heat's own share: the error with the fire less the error without it.
+                e = _booking_error_pct(rows[m], m) - _booking_error_pct(base_rows[m], m)
+                errs[m].append(e)
+                print(f"  fire {kw:4.1f} kW from {h0:02d}:00 ({fire_kwh:.1f} kWh_th): plan {plan_kwh:.2f} drawn {drawn_kwh:.2f};"
+                      f" m {m}: calibration {rows[m]['meter_calibration']} pct {rows[m]['savings_pct']}"
+                      f" (no fire {base_rows[m]['savings_pct']}); booking error from the heat {e:+.2f} %")
+    for m, e in errs.items():
+        a = np.asarray(e)
+        print(f"RESULT wood_plant_error_m{m}: mean {a.mean():+.2f} % min {a.min():+.2f} max {a.max():+.2f} sd {a.std():.2f} over {a.size} fires")
+    # The perturbation: the same largest fire with the pump blind to it, the
+    # meter at the plan's power; the error from the heat must read zero.
+    blind, *_ = plant_loop(lambda t: 12.0 if 17 <= t.hour < 17 + FIRE_HOURS else 0.0, price, respond=False)
+    print("  perturbation (pump blind to the fire): "
+          + ", ".join(f"m {m} error {_booking_error_pct(blind[m], m) - _booking_error_pct(base_rows[m], m):+.2f} %"
+                      for m in METER_OVER_MODEL))
+
+
 ARMS = {
     "first": first_step,
     "valve-flat": lambda: valve_arm("flat"),
@@ -229,6 +380,7 @@ OWED = {
     "wood-fire": lambda: closed_loop(True, lambda t: 12.0 if 17 <= t.hour < 21 else 0.0, 40.0, 30.0),
     "wood-stale": lambda: closed_loop(True, lambda t: 0.0, 28.0, 27.3),
     "wood-coast": lambda: closed_loop(True, lambda t: 0.0, 75.0, 30.0),
+    "wood-plant": wood_plant,
 }
 
 
diff --git a/dev/programme/delivery/3244.md b/dev/programme/delivery/3244.md
new file mode 100644
index 000000000..2fc991dd8
--- /dev/null
+++ b/dev/programme/delivery/3244.md
@@ -0,0 +1 @@
+- [#3244](https://github.com/tvofi/heatpump_optimizer/pull/3244) — **open**, R10-HOTFIX-SAV-ESTIMATE: the monthly receipt says wood heat counts in the saving (R10-HOTFIX-SAV-ESTIMATE)
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index fb55a7234..9349a7ea0 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -885,7 +885,17 @@ safe-temperature headroom, so the plan keeps charging cheap hours right through
 a burn. Heat still in the wood tank at day's end counts in the thermal-battery
 view, up to 95 °C. The savings reference has no wood at all, so wood's heat
 counts in the saving and firewood's cost is not counted; the savings page says
-so where wood is configured. Without the probe, or
+so where wood is configured. The reference is scaled to the meter, and on a
+wood house that scale only raises it, so a meter that falls under the plan
+during a fire cannot cancel wood's heat. A fire the plan did not foresee moves
+the meter off the plan only until the next re-plan reads the warmer tank. In a
+simulated house (the `wood-plant` arm of
+`dev/audit/harnesses/r10_sav_wood_reference.py`: 4 to 12 kW, 4-hour fires,
+each plan held an hour, where the integration re-plans every interval), the
+pump drew between 0 and 4.5 % less than its plan.
+Where the model reads the meter low, the reference is booked low by that
+share, so the saving is understated by up to that much. Where the model reads
+the meter high, the reference is not scaled down at all on a wood house. Without the probe, or
 while it is stale, the wood tank is not a store of its own: the model keeps the
 one buffer tank, and a burn is the bounded free heat described above.
 
diff --git a/tests/card.mjs b/tests/card.mjs
index 79e43c934..f8adac8fd 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -2828,6 +2828,26 @@ check("the hand-scheduled reason has a label",
     /Covers spot energy, grid energy fee, capacity charge\. The savings figure compares spot cost only\./.test(rcpPage));
   check("UX-6: the saving against a thermostat is the month's own row",
     /Saved 148\.00 SEK \(19 %\) against a plain thermostat/.test(rcpPage));
+  // R10-SAV-WOOD-HEAT (owner ruling, 2026-11-04): the reference has no wood, so
+  // on a house with wood configured the receipt's saving states, beside the
+  // figure, that it includes wood's heat and not firewood's cost, in en and sv.
+  // The null control is the page above: no wood configured, no disclaimer.
+  const rcpWood = (lang) => {
+    const st = JSON.parse(JSON.stringify(rcpStates));
+    st[DEFAULT_SPACE].attributes.wood_fuel = { ready: true, cheaper: false, show_whatif: true, slots: [] };
+    const c = build(st);
+    c.hass = { states: st, language: lang };
+    c._onCardClick({});
+    c.dialog.page = "savings";
+    c._render();
+    return collect(c.shadowRoot).join("\n");
+  };
+  const rcpWoodNote = (page) => (page.match(/receipt-wood-note">([^<]*)/) || [])[1] || "";
+  check("the receipt's saving on a wood house says it includes wood's heat, not firewood's cost (en, sv); none without wood",
+    rcpWoodNote(rcpWood("en")) === "The saving includes heat from wood. Firewood's cost is not counted." &&
+    rcpWoodNote(rcpWood("sv-SE")) === "Sparandet inkluderar värme från ved. Vedens kostnad räknas inte." &&
+    !/receipt-wood-note/.test(rcpPage),
+    `${rcpWoodNote(rcpWood("en"))} | ${rcpWoodNote(rcpWood("sv-SE"))}`);
   check("UX-6: the money goes by reason, largest first",
     /Where the money went/.test(rcpPage) &&
     rcpPage.indexOf("Cheapest hours") < rcpPage.indexOf("Keeping the house at target"));
diff --git a/tests/features.py b/tests/features.py
index 22bb32fca..65bee0062 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -44097,6 +44097,31 @@ R.check(
     and "baseline_kw" not in _pub,
     repr({k: _pub.get(k) for k in ("savings_months", "baseline_power_schedule")}),
 )
+
+
+# R10-SAV-WOOD-HEAT: the published row takes the wood floor from the house's
+# own configuration, read where the coordinator publishes it (a meter at half
+# the plan books 75 % on a wood house, 50 % on a plain one: _sb_meter_row's).
+def _sv_published_pct(**config):
+    coord = _t2_coord(**config)
+    for hour in range(24):
+        coord._ledger.observe_spot_and_settle_savings(
+            _SavDT(2026, 2, 9, hour, 0), 1.0, {"baseline_kw": 2.0, "power": 1.0}, 0.5, 1.0
+        )
+    try:
+        _dt_sav.now = lambda: NOW
+        rows = coord._build_data_dict()["savings_months"]
+    finally:
+        _dt_sav.now = _real_now_sav
+    return next(r["savings_pct"] for r in rows if r["month"] == "2026-02")
+
+
+_sv_wood_pub = (_sv_published_pct(wood_furnace_enabled=True), _sv_published_pct())
+R.check(
+    "the coordinator publishes the wood floor from the house's configuration, and no floor without wood",
+    _sv_wood_pub == (75.0, 50.0),
+    repr(_sv_wood_pub),
+)
 _sv._current_action = {"power": 1.0, "dhw_power": 0.5, "baseline_kw": 3.25}
 # Drive the pending builder by reading the assignment target after a call
 # is not possible without the interval loop; pin the source instead:

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
