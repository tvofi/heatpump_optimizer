# Review packet #3244
head: 8bc540e052a8a4ac048715d4d2e7d0ab9a260c08
base: 28482eceeb6b9809e44b12d80fc994282cc21645

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=128216329154 neutral
arch-score / arch-score id=128218194827 success
arm id=128215911060 skipped
budget-raise-gate / budget-raise-gate id=128218194791 success
cancel-superseded id=128217982162 success
codeql id=128218196267 skipped
codeql / Analyze (actions) id=128216096389 success
codeql / Analyze (javascript-typescript) id=128216096394 success
codeql / Analyze (python) id=128216096339 in_progress
gate id=128218621028 in_progress
governance id=128218195859 skipped
governance / delivery-status id=128216096490 success
governance / delivery-status-publish id=128216097952 skipped
governance / env-matrix id=128216096387 success
governance / instrument-self-tests id=128216096422 in_progress
governance / policy-docs id=128216096448 success
governance / record id=128216097788 skipped
governance / wave-script id=128216096449 success
hassfest id=128218196658 skipped
hassfest / hassfest id=128216096248 success
kernel-points id=128218196857 skipped
pr-contract id=128218622296 skipped
prelude id=128217982000 success
refresh id=128217981682 success
tests id=128218196280 skipped
tests / arch-instrument id=128216321989 success
tests / briefs id=128216096534 success
tests / browser id=128216322062 success
tests / closure-scope id=128216096305 success
tests / closures id=128216322079 in_progress
tests / coverage id=128216322085 in_progress
tests / fast (3.14) id=128216322020 in_progress
tests / mutation id=128216096396 in_progress
tests / nightly-ha id=128216323455 skipped
tests / nightly-status id=128216096489 success
tests / replay id=128216321970 in_progress
tests / typing id=128216322061 success
validate id=128218196112 skipped
validate / validate-hacs id=128216096474 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 661322b8: dismissed:owner ruling territory, stated for the owner in docs/how-it-works.md and this body
NOTE body item 33581d9d: dismissed:a dispatch event, recorded for the orchestrator in this body
NOTE body item 6f451c44: dismissed:a session plugin outside this repository's policy
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified git checkout
             `git checkout` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git show dea3c729:blueprints/automation/notifications.yaml
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py wood-plant
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_rca_sav_estimate.py census
             `dev/audit/harnesses/r10_rca_sav_estimate.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 -I tools/policy/agreement_py.py --out <json> && node tools/policy/agreement.mjs --py-json <json>
             `tools/policy/agreement_py.py` is in the tree at this head
  ok         python3 -I tools/policy/agreement_py.py --out <json> && node tools/policy/agreement.mjs --py-json <json>
             `tools/policy/agreement.mjs` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         node tools/policy/agreement.mjs --self-test
             `tools/policy/agreement.mjs` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  unverified git diff --quiet origin/main HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md tests/golden/card_claimed_drift.txt
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 13 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/saving_includes_wood.RETURN_DEL.62b7ac43.json b/tests/mutation_ledger/killed_by/wood_fuel.py/saving_includes_wood.RETURN_DEL.62b7ac43.json
new file mode 100644
index 000000000..0777cf5c5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/wood_fuel.py/saving_includes_wood.RETURN_DEL.62b7ac43.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:saving_includes_wood RETURN_DEL 62b7ac43",
+  "killed_by": "tests/features.py",
+  "old": "    return bool((data.get(\"wood_fuel\") or {}).get(\"show_whatif\"))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}


## Three-dot diff
diff --git a/README.md b/README.md
index 6418a5b7e..62144b79b 100644
--- a/README.md
+++ b/README.md
@@ -585,7 +585,7 @@ every sensor is created on every install regardless of which group it is in.
 | Cost Predicted | CUR | Cost of the optimized 24 h plan | |
 | Cost Baseline | CUR | Cost of the baseline over the same 24 h | |
 | DHW Heating Cost (next 24 h) | CUR | Estimated cost of the planned hot water | |
-| Plan Monthly Savings | CUR | Estimated savings for the open month, with the settled and in-progress months in attributes | Unavailable until at least one month row exists |
+| Plan Monthly Savings | CUR | Estimated savings for the open month, with the settled and in-progress months in attributes; `saving_includes_wood` is `true` where wood is configured, because the saving then includes wood's heat and not firewood's cost | Unavailable until at least one month row exists |
 | Cost Contract Comparison | CUR/kWh | How far below the month's flat-consumer average the shifting landed; the three settled totals — hourly spot, monthly-average spot, fixed price — ride in attributes | Diagnostic; disabled by default; needs a configured contract comparison |
 | Lifetime Space Heating Cost | CUR | Accumulating cost | |
 | DHW Cost (lifetime) | CUR | Accumulating cost | |
diff --git a/blueprints/automation/notifications.yaml b/blueprints/automation/notifications.yaml
index c6abe36af..f14ac0a66 100644
--- a/blueprints/automation/notifications.yaml
+++ b/blueprints/automation/notifications.yaml
@@ -121,6 +121,9 @@ action:
                 {% if data.saving_pct is not none
                 %}({{ data.saving_pct | round(0) }} %) {% endif
                 %}less than a plain thermostat would have{% endif %}.
+                {%- if data.saving_sek is not none and data.saving_includes_wood %}
+                The saving includes heat from wood. Firewood's cost is not counted.
+                {%- endif %}
       - alias: Comfort at risk
         conditions:
           - "{{ trigger.event.event_type == 'heatpump_optimizer_comfort_at_risk' }}"
diff --git a/custom_components/heatpump_optimizer/notifier.py b/custom_components/heatpump_optimizer/notifier.py
index 38f662f70..a8febd212 100644
--- a/custom_components/heatpump_optimizer/notifier.py
+++ b/custom_components/heatpump_optimizer/notifier.py
@@ -38,6 +38,7 @@ from homeassistant.util import dt as dt_util
 from .const import CONF_FLOOR_RETURN_TEMP_ENTITY, DOMAIN
 from .payload import InputProblem, Payload
 from .issues import set_issue
+from .wood_fuel import saving_includes_wood
 from .store import QuarantiningStore, load_mapping
 
 _LOGGER = logging.getLogger(__name__)
@@ -100,7 +101,7 @@ def _monthly_receipt(data: Payload) -> Detected:
         # has no saving, and with wood configured the saving includes its heat
         # and not its cost.
         "saving_old_basis": bool(saving and saving.get("old_basis")),
-        "saving_includes_wood": bool((data.get("wood_fuel") or {}).get("show_whatif")),
+        "saving_includes_wood": saving_includes_wood(data),
     })}
 
 
diff --git a/custom_components/heatpump_optimizer/sensor.py b/custom_components/heatpump_optimizer/sensor.py
index 3375c846a..4ef511883 100644
--- a/custom_components/heatpump_optimizer/sensor.py
+++ b/custom_components/heatpump_optimizer/sensor.py
@@ -53,6 +53,7 @@ from .entry_config import EntryConfig
 from .payload import Payload
 from .mixing_valve import is_throttling
 from .thermal_model import feedback_gaps
+from .wood_fuel import saving_includes_wood
 
 if TYPE_CHECKING:
     _SensorMixinBase = HeatPumpOptimizerEntity
@@ -520,6 +521,9 @@ class MonthlySavingsSensor(_WaitsForEvidenceMixin, HeatPumpOptimizerSensorBase):
             "savings_months": self._rows(),
             "receipts": data.get("receipts") or [],
             "plan_replay": data.get("plan_replay"),
+            # The state is the metered saving the receipt states: with wood
+            # configured it includes wood's heat and not firewood's cost.
+            "saving_includes_wood": saving_includes_wood(data),
         }
         waiting = self._waiting_for
         if waiting is not None:
diff --git a/custom_components/heatpump_optimizer/wood_fuel.py b/custom_components/heatpump_optimizer/wood_fuel.py
index 6af6a1090..c732f9602 100644
--- a/custom_components/heatpump_optimizer/wood_fuel.py
+++ b/custom_components/heatpump_optimizer/wood_fuel.py
@@ -91,6 +91,16 @@ def wood_furnace_on(config: Mapping[str, Any]) -> bool:
     return wood_furnace_inferred(config)
 
 
+def saving_includes_wood(data: Mapping[str, Any]) -> bool:
+    """Whether the payload's metered saving includes wood's heat.
+
+    The reference has no wood, so where wood is configured the saving counts
+    its heat and not firewood's cost (owner ruling, 2026-11-04). Every surface
+    stating that saving reads this one definition.
+    """
+    return bool((data.get("wood_fuel") or {}).get("show_whatif"))
+
+
 def wood_fuel_ready(config: Mapping[str, Any]) -> bool:
     if not wood_furnace_on(config):
         return False
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index a638cf7c4..c1a852288 100644
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
diff --git a/dev/audit/harnesses/r10_sav_receipt_render.py b/dev/audit/harnesses/r10_sav_receipt_render.py
new file mode 100644
index 000000000..e8335b805
--- /dev/null
+++ b/dev/audit/harnesses/r10_sav_receipt_render.py
@@ -0,0 +1,91 @@
+#!/usr/bin/env python3
+"""R10-HOTFIX-SAV-ESTIMATE: the notifications blueprint's monthly receipt, rendered.
+
+WHY IT EXISTS. The receipt event (``notifier.EVENT_MONTHLY_RECEIPT``) carries
+``saving_includes_wood``, and the blueprint's "Monthly receipt" message states
+the event's ``saving_sek`` to the user. Where wood is configured that saving
+includes wood's heat and not firewood's cost, so the message must say so (Carry
+A, tvofi 2026-11-04). ``tests/entities.py`` pins the template's source, because
+CI's interpreter has no jinja2; this harness renders it, under an interpreter
+that has one (``/opt/hpo/venv-ha/bin/python``, whose Home Assistant brings
+jinja2), so a reader sees the message a user receives.
+
+Asserted arms (rc 1 on DEFECT):
+
+  wood      a saving on a wood house: the card's ``savings.wood_note`` appears
+            exactly once in the rendered message.
+  no-wood   the null leg: the same saving, ``saving_includes_wood`` false, and
+            the note is absent.
+  no-saving the event's ``saving_sek`` is null on a wood house: the message
+            states no saving, so it carries no note.
+
+Usage: python3 dev/audit/harnesses/r10_sav_receipt_render.py [blueprint.yaml]
+The default blueprint is the tree's; pass another file (a ``git show`` of an
+older head) to measure that one.
+"""
+from __future__ import annotations
+
+import pathlib
+import re
+import sys
+
+import jinja2
+import yaml
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
+ROOT = repo_root(__file__)
+DEFAULT_BP = ROOT / "blueprints/automation/notifications.yaml"
+CARD = ROOT / "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
+
+
+class _Loader(yaml.SafeLoader):
+    pass
+
+
+_Loader.add_constructor("!input", lambda loader, node: loader.construct_scalar(node))
+
+
+def receipt_message(path: pathlib.Path) -> str:
+    bp = yaml.load(path.read_text(), Loader=_Loader)
+    return next(
+        option["sequence"][0]["data"]["message"]
+        for step in bp["action"] if "choose" in step
+        for option in step["choose"] if option.get("alias") == "Monthly receipt"
+    )
+
+
+def main() -> int:
+    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BP
+    note = re.search(r'"savings\.wood_note": "([^"]+)"', CARD.read_text()).group(1)
+    template = jinja2.Environment().from_string(receipt_message(path))
+    base = {"total_sek": 812.4, "currency": "SEK", "saving_sek": 203.6, "saving_pct": 20.1}
+    arms = [
+        ("wood", {"saving_includes_wood": True}, 1),
+        ("no-wood", {"saving_includes_wood": False}, 0),
+        ("no-saving", {"saving_sek": None, "saving_includes_wood": True}, 0),
+    ]
+    defect = False
+    for name, extra, want in arms:
+        text = template.render(data={**base, **extra})
+        got = text.count(note)
+        ok = got == want
+        defect |= not ok
+        print(f"RESULT {name} notes={got} want={want} {'ok' if ok else 'DEFECT'} message={text!r}")
+    return 1 if defect else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
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
diff --git a/docs/automations.md b/docs/automations.md
index 7ed7f4ea5..58205f5eb 100644
--- a/docs/automations.md
+++ b/docs/automations.md
@@ -178,5 +178,5 @@ Blueprints → Import Blueprint:
 - [Charge an EV from grid headroom](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/charge_ev_from_grid_headroom.yaml) — from the first example above.
 - [Economy mode through the evening price peak](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/economy_mode_on_price_peak.yaml) — from the second example above.
 - [Notify when a manual plan takes over](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notify_on_manual_plan.yaml) — from the third example above.
-- [Notifications](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notifications.yaml) — sends the five events above to a notify target, one switch per event, with quiet hours that the comfort alert passes through.
+- [Notifications](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notifications.yaml) — sends the five events above to a notify target, one switch per event, with quiet hours that the comfort alert passes through. Where wood is configured, the monthly receipt's message says the saving includes heat from wood and that firewood's cost is not counted (`saving_includes_wood`).
 - [Notify when wood beats the heat pump today](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notify_wood_cheaper_window.yaml) — one phone notification on a day the plan expects firewood to be cheaper than the heat pump, naming the cheaper windows (the Wood Cheaper Than Heat Pump sensor's `cheaper_windows` attribute) and when to light the furnace (`lighting_start` to `lighting_end`, opened by the wood page's lead time before the first window), with an optional follow-up when a replan brings a window that is not yet open and overlaps none the plan had before (a moved or split window sends nothing), and no follow-up after a configurable time, 21:00 by default. Silent on a day with none.
diff --git a/docs/dashboard-card.md b/docs/dashboard-card.md
index 6002f2a17..7c5f7f8d3 100644
--- a/docs/dashboard-card.md
+++ b/docs/dashboard-card.md
@@ -559,7 +559,10 @@ neither column. At one flat price the difference is energy alone. The savings co
 carries a bar scaled to the biggest month in the table, which answers "compared
 with the others" without quoting a target the page does not show. The open
 month is an estimate until it closes, and is badged as one; a month with no
-settled rows yet says so in words rather than drawing an empty table.
+settled rows yet says so in words rather than drawing an empty table. The
+baseline has no wood, so where wood is configured the receipt and the table
+both say the saving includes heat from wood and that firewood's cost is not
+counted.
 
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="img/card/savings-dark.png">
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index fb55a7234..0518284f8 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -884,8 +884,19 @@ for water the pump never made — and cannot eat the buffer's
 safe-temperature headroom, so the plan keeps charging cheap hours right through
 a burn. Heat still in the wood tank at day's end counts in the thermal-battery
 view, up to 95 °C. The savings reference has no wood at all, so wood's heat
-counts in the saving and firewood's cost is not counted; the savings page says
-so where wood is configured. Without the probe, or
+counts in the saving and firewood's cost is not counted; the savings page, the
+Plan Monthly Savings sensor and the notifications blueprint's monthly receipt
+say so where wood is configured. The reference is scaled to the meter, and on a
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
diff --git a/tests/closures.json b/tests/closures.json
index 79d3291ae..1ba567ff3 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4094,6 +4094,7 @@
    "dev/audit/harnesses/r10_sav_baseline_mutants.py",
    "dev/audit/harnesses/r10_sav_null_settled.py",
    "dev/audit/harnesses/r10_sav_null_terms.py",
+   "dev/audit/harnesses/r10_sav_receipt_render.py",
    "dev/audit/harnesses/r10_sav_volume.py",
    "dev/audit/harnesses/r10_sav_wood_reference.py",
    "dev/audit/harnesses/r10_savings_upgrade_month.py",
diff --git a/tests/entities.py b/tests/entities.py
index 1a257bf95..561ad0b5b 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -12362,6 +12362,73 @@ R.check(
     == _ATTR_RICH["savings_months"],
     repr(_ready_sav.native_value),
 )
+# R10-SAV-WOOD-HEAT (owner ruling, 2026-11-04): the reference has no wood, so on
+# a house with wood configured the entity's saving says it includes wood's heat
+# and not firewood's cost, by the receipt event's one definition. The null
+# controls: no wood_fuel at all, and wood not configured, both state False.
+from heatpump_optimizer.notifier import _monthly_receipt as _sav_receipt  # noqa: E402
+from heatpump_optimizer import notifier as _sav_notifier  # noqa: E402
+
+
+def _sav_wood(fuel):
+    data = {k: v for k, v in _ATTR_RICH.items() if k != "wood_fuel"}
+    if fuel is not None:
+        data["wood_fuel"] = fuel
+    attrs = sensor.MonthlySavingsSensor(FakeCoordinator(data), ENTRY).extra_state_attributes
+    month = data["savings_months"][0]["month"]
+    event = _sav_receipt({**data, "insight": {"monthly_report": {"month": month}}})
+    return attrs.get("saving_includes_wood"), event["receipt"].data["saving_includes_wood"]
+
+
+_sav_wood_cases = (
+    _sav_wood({"ready": True, "show_whatif": True}),
+    _sav_wood({"ready": False, "show_whatif": False}),
+    _sav_wood(None),
+)
+R.check(
+    "MonthlySavingsSensor states that a wood house's saving includes wood's heat, as the receipt event does; "
+    "False without wood",
+    _sav_wood_cases == ((True, True), (False, False), (False, False)),
+    repr(_sav_wood_cases),
+)
+
+
+# The receipt event leaves the package for the notifications blueprint, whose
+# Monthly receipt message states the same saving to the user, so it carries the
+# same statement, guarded by the event's saving_includes_wood and worded as the
+# card's savings.wood_note. A source pin, not a render: CI's interpreter has no
+# jinja2. The guard is the null leg -- a house without wood gets no statement.
+class _SavBpLoader(yaml.SafeLoader):
+    pass
+
+
+_SavBpLoader.add_constructor("!input", lambda loader, node: loader.construct_scalar(node))
+_sav_bp_root = pathlib.Path(__file__).resolve().parents[1]
+_sav_bp = yaml.load(
+    (_sav_bp_root / "blueprints/automation/notifications.yaml").read_text(),
+    Loader=_SavBpLoader,
+)
+_sav_bp_msg = next(
+    option["sequence"][0]["data"]["message"]
+    for step in _sav_bp["action"] if "choose" in step
+    for option in step["choose"] if option.get("alias") == "Monthly receipt"
+)
+_sav_bp_note = re.search(
+    r'"savings\.wood_note": "([^"]+)"',
+    (_sav_bp_root / ROOT / "www/heatpump-optimizer-card.js").read_text(),
+).group(1)
+R.check(
+    "The notifications blueprint's monthly receipt says a wood house's saving includes wood's heat, "
+    "in the card's words, and says nothing without wood",
+    "saving_includes_wood" in _sav_notifier.EVENT_DATA[_sav_notifier.EVENT_MONTHLY_RECEIPT]
+    and _sav_bp_msg.count(_sav_bp_note) == 1
+    and re.search(
+        r"\{%-? if data\.saving_sek is not none and data\.saving_includes_wood %\}\s*"
+        + re.escape(_sav_bp_note) + r"\s*\{%-? endif %\}",
+        _sav_bp_msg,
+    ) is not None,
+    _sav_bp_msg,
+)
 
 
 #: The one publisher whose attribute KEYS are data rather than API:
@@ -12521,7 +12588,8 @@ _PUBLISHED_ATTRS: dict[str, frozenset[str]] = {
         "outage_recovery_active", "projected_peak_cost", "projected_peak_kw"
     }),
     "MonthlySavingsSensor": frozenset(
-        {"plan_replay", "receipts", "savings_months", "waiting_for"}
+        {"plan_replay", "receipts", "saving_includes_wood", "savings_months",
+         "waiting_for"}
     ),
     "ObservedCOPSensor": frozenset({
         "cop_samples", "cop_scale", "defrost_buckets", "defrost_derate",
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
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 5d13c639a..5edc01f60 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -67,6 +67,11 @@
 # v7.1.4: release and audit machinery: stamp base, gate lease. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
+coord_all_features # R10-SAV-WOOD-HEAT: the monthly-savings sensor publishes saving_includes_wood (true on the wood house, false elsewhere); one key added, no value moved; structure-only edit of the committed file, never recorded
+coord_dhw # R10-SAV-WOOD-HEAT: the monthly-savings sensor publishes saving_includes_wood (true on the wood house, false elsewhere); one key added, no value moved; structure-only edit of the committed file, never recorded
+coord_grid_fee # R10-SAV-WOOD-HEAT: the monthly-savings sensor publishes saving_includes_wood (true on the wood house, false elsewhere); one key added, no value moved; structure-only edit of the committed file, never recorded
+coord_minimal # R10-SAV-WOOD-HEAT: the monthly-savings sensor publishes saving_includes_wood (true on the wood house, false elsewhere); one key added, no value moved; structure-only edit of the committed file, never recorded
+coord_two_zone # R10-SAV-WOOD-HEAT: the monthly-savings sensor publishes saving_includes_wood (true on the wood house, false elsewhere); one key added, no value moved; structure-only edit of the committed file, never recorded
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
diff --git a/tests/golden/coord_all_features.json b/tests/golden/coord_all_features.json
index 0174eb088..19dc6fe35 100644
--- a/tests/golden/coord_all_features.json
+++ b/tests/golden/coord_all_features.json
@@ -2189,6 +2189,7 @@
    "extra_state_attributes": {
     "plan_replay": null,
     "receipts": [],
+    "saving_includes_wood": true,
     "savings_months": [],
     "waiting_for": "settled_savings_month"
    },
diff --git a/tests/golden/coord_dhw.json b/tests/golden/coord_dhw.json
index f82b3bcdf..c3a004a9b 100644
--- a/tests/golden/coord_dhw.json
+++ b/tests/golden/coord_dhw.json
@@ -2110,6 +2110,7 @@
    "extra_state_attributes": {
     "plan_replay": null,
     "receipts": [],
+    "saving_includes_wood": false,
     "savings_months": [],
     "waiting_for": "settled_savings_month"
    },
diff --git a/tests/golden/coord_grid_fee.json b/tests/golden/coord_grid_fee.json
index 71eb46759..bd082b312 100644
--- a/tests/golden/coord_grid_fee.json
+++ b/tests/golden/coord_grid_fee.json
@@ -1949,6 +1949,7 @@
    "extra_state_attributes": {
     "plan_replay": null,
     "receipts": [],
+    "saving_includes_wood": false,
     "savings_months": [],
     "waiting_for": "settled_savings_month"
    },
diff --git a/tests/golden/coord_minimal.json b/tests/golden/coord_minimal.json
index 9246a0920..454f8bfee 100644
--- a/tests/golden/coord_minimal.json
+++ b/tests/golden/coord_minimal.json
@@ -1949,6 +1949,7 @@
    "extra_state_attributes": {
     "plan_replay": null,
     "receipts": [],
+    "saving_includes_wood": false,
     "savings_months": [],
     "waiting_for": "settled_savings_month"
    },
diff --git a/tests/golden/coord_two_zone.json b/tests/golden/coord_two_zone.json
index d1a0347d0..a4f37477a 100644
--- a/tests/golden/coord_two_zone.json
+++ b/tests/golden/coord_two_zone.json
@@ -1995,6 +1995,7 @@
    "extra_state_attributes": {
     "plan_replay": null,
     "receipts": [],
+    "saving_includes_wood": false,
     "savings_months": [],
     "waiting_for": "settled_savings_month"
    },
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/saving_includes_wood.RETURN_DEL.62b7ac43.json b/tests/mutation_ledger/killed_by/wood_fuel.py/saving_includes_wood.RETURN_DEL.62b7ac43.json
new file mode 100644
index 000000000..0777cf5c5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/wood_fuel.py/saving_includes_wood.RETURN_DEL.62b7ac43.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:saving_includes_wood RETURN_DEL 62b7ac43",
+  "killed_by": "tests/features.py",
+  "old": "    return bool((data.get(\"wood_fuel\") or {}).get(\"show_whatif\"))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tools/policy/agreement.mjs b/tools/policy/agreement.mjs
index 5618678e4..a43372b98 100644
--- a/tools/policy/agreement.mjs
+++ b/tools/policy/agreement.mjs
@@ -587,6 +587,8 @@ const SHARED_GRAMMARS = {
   "[0-9a-f]{40}": "not-a-concept:the full commit-SHA shape, policy_lint.mjs's head check and ci_probe.py's probe-push guard",
   "DERIVED=\\$\\(.*?\\)": "identical:coverage_tree.sh's DERIVED line extractor, entities.py _cir_once_count and the disclosed copy in U5b's script_runs.py null control",
   "fast\\)\\s+(SCRIPTS=.*?) ;;": "identical:coverage_tree.sh's `fast)` SCRIPTS extractor, entities.py _cir_once_count and the disclosed copy in U5b's script_runs.py null control",
+  // R10-HOTFIX-SAV-ESTIMATE: the blueprint's receipt reuses the card's wood note.
+  '"savings\\.wood_note": "([^"]+)"': "identical:the card's en savings.wood_note extractor, entities.py's blueprint receipt pin and the render harness r10_sav_receipt_render.py",
 }
 
 const isGovernanceCode = (f) => /\.(py|mjs|js|cjs)$/.test(f)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
