# Review packet #2997
head: 7c43d8fb1505320e2b10d7c122dab3215ebd085c
base: e77418f9b48f89421bd72b0ab511c057341c7fa4

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=124122696718 neutral
arch-score / arch-score id=124122284725 success
arm id=124122045972 skipped
budget-raise-gate / budget-raise-gate id=124122285155 success
cancel-superseded id=124122042231 success
codeql / Analyze (actions) id=124122284943 success
codeql / Analyze (javascript-typescript) id=124122285262 in_progress
codeql / Analyze (python) id=124122285048 in_progress
governance / delivery-status id=124122285211 success
governance / delivery-status-publish id=124122288103 skipped
governance / env-matrix id=124122285241 in_progress
governance / instrument-self-tests id=124122285150 in_progress
governance / policy-docs id=124122285208 in_progress
governance / record id=124122288029 skipped
governance / wave-script id=124122285094 success
hassfest / hassfest id=124122285271 success
kernel-points id=124122287992 skipped
prelude id=124122041641 success
refresh id=124122042229 success
tests / arch-instrument id=124122578310 in_progress
tests / briefs id=124122284922 success
tests / browser id=124122578323 in_progress
tests / closure-scope id=124122285212 success
tests / closures id=124122578565 in_progress
tests / coverage id=124122578469 in_progress
tests / fast (3.14) id=124122578583 in_progress
tests / mutation id=124122284888 failure
tests / mutation-autofix id=124123187126 in_progress
tests / mutation-pins (1) id=124122741883 success
tests / nightly-ha id=124122581379 skipped
tests / nightly-status id=124122285054 success
tests / replay id=124122581600 skipped
tests / typing id=124122578351 in_progress
validate / validate-hacs id=124122285267 success

## Refusals
red-unanswered: concluded red check `tests / mutation` is not named in ## Red checks

## Advisories
none

## carry_audit at the head
NOTE body item 8b9a72b3: R10-UX-HEALTH
NOTE body item 37525a9d: R10-UX-HEALTH
NOTE body item 45460f32: R10-UX-HEALTH
NOTE body item aa906295: R10-UX-HEALTH
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified inked.
             no segment of this names a program this check knows
  unverified share ink` FAILs with 30 entries.
             no segment of this names a program this check knows
  unverified px. That is 3 pairs in each of the five 375-px cells: light/en,
             no segment of this names a program this check knows
  unverified light/sv-SE, dark/en, dark-on-light, light-on-dark. Each cell has text
             no segment of this names a program this check knows
  unverified "0" x "1" (4 px), "1" x "2" (2 px) and "2" x "3" (4 px).
             no segment of this names a program this check knows
  unverified each entry.
             no segment of this names a program this check knows
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_demand_overbook.py
             `dev/audit/harnesses/r10_demand_overbook.py` is in the tree at this head
  ok         node tests/card_browser.mjs
             `tests/card_browser.mjs` is in the tree at this head

FIGURES: 4 resolved, 6 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.BOOLOP.85c924c9.json b/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.BOOLOP.85c924c9.json
deleted file mode 100644
index 9d0c8f315..000000000
--- a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.BOOLOP.85c924c9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/button.py:DebugFinalizeButton.extra_state_attributes BOOLOP 85c924c9",
-  "killed_by": "tests/debug_collect.py",
-  "old": "        if collector is not None and not collector.final:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fc76a05577985c92574e4d42433f61192efe47f4: BOOLOP (`if collector is not None or not collector.final:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.GUARD_OFF.85c924c9.json b/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.GUARD_OFF.85c924c9.json
deleted file mode 100644
index f190391ef..000000000
--- a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.GUARD_OFF.85c924c9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/button.py:DebugFinalizeButton.extra_state_attributes GUARD_OFF 85c924c9",
-  "killed_by": "tests/debug_collect.py",
-  "old": "        if collector is not None and not collector.final:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fc76a05577985c92574e4d42433f61192efe47f4: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.RETURN_DEL.3dca65c8.json b/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.RETURN_DEL.3dca65c8.json
deleted file mode 100644
index 266443142..000000000
--- a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.RETURN_DEL.3dca65c8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/button.py:DebugFinalizeButton.extra_state_attributes RETURN_DEL 3dca65c8",
-  "killed_by": "tests/debug_collect.py",
-  "old": "        return {\"waiting_for\": \"debug_collect\"}",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fc76a05577985c92574e4d42433f61192efe47f4: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/button.py b/custom_components/heatpump_optimizer/button.py
index 9d068bda0..c412d9ea0 100644
--- a/custom_components/heatpump_optimizer/button.py
+++ b/custom_components/heatpump_optimizer/button.py
@@ -216,11 +216,18 @@ class DebugFinalizeButton(_OptimizerButtonBase):
 
     @property
     def extra_state_attributes(self) -> dict[str, str]:
-        """Why the button is dark on an install that is not collecting (#1335)."""
+        """Why the button is dark: the option is off (#1335), or the collection
+        has finished and waits for the `debug_collect` action's `start` (#2809).
+
+        Home Assistant drops these while the button is unavailable; the card's
+        Health row is the surface a person sees.
+        """
         collector = debugger.collector_for(self.coordinator)
-        if collector is not None and not collector.final:
-            return {}
-        return {"waiting_for": "debug_collect"}
+        if collector is None:
+            return {"waiting_for": "debug_collect"}
+        if collector.final:
+            return {"waiting_for": "debug_collect_start"}
+        return {}
 
     async def async_press(self) -> None:
         """Returns at once; the self-tests the stop starts run in the background (#1940)."""
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index 8e8501dcf..7d764017d 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -231,10 +231,10 @@ const STRINGS = {
     "health.cop_reason_span_too_long": "The meter span ran too long to use.",
     "health.metric_heat_loss": "How fast the house loses heat, in watts per degree of difference between inside and outside. Higher is a leakier house; with no samples it is the settings' estimate.",
     "health.metric_solar": "How much of the sun's heat the windows let in, against the settings. Above 1 lets in more; with no samples it is the settings' value.",
-    "health.metric_lower": "The lower floor's heat loss as a share of the settings' estimate.",
-    "health.metric_tank": "How fast the hot-water tank cools when the pump is off, in °C per hour. Lower is better insulated.",
+    "health.metric_lower": "The lower floor's heat loss as a share of the settings' estimate. Above 100 % loses more; with no samples it is the settings' estimate.",
+    "health.metric_tank": "How fast the hot-water tank cools when the pump is off, in °C per hour. Lower is better insulated; with no samples it is the default rate.",
     "health.metric_cop": "Whether the heat pump still delivers as much heat per kWh as it used to. A dash means it is not yet watched.",
-    "health.metric_gains": "Heat from people, cooking and appliances by hour of day, which the plan counts as free heating.",
+    "health.metric_gains": "Heat from people, cooking and appliances by hour of day, in kW, which the plan counts as free heating. Higher bars are more free heat; with no samples the plan counts none.",
     "health.debug_title": "Debug collection",
     "health.debug_off": "Off. When a bug report asks for one, Start records a week of cycles into the diagnostics file.",
     "health.debug_active": "Collecting: {rows} records so far, about {days} days left.",
@@ -1073,10 +1073,10 @@ const STRINGS = {
     "health.cop_reason_span_too_long": "Mätarens intervall blev för långt för att användas.",
     "health.metric_heat_loss": "Hur snabbt huset förlorar värme, i watt per grads skillnad mellan inne och ute. Högre är ett otätare hus; utan mätningar är det inställningarnas uppskattning.",
     "health.metric_solar": "Hur mycket av solens värme fönstren släpper in, mot inställningarna. Över 1 släpper in mer; utan mätningar är det inställningarnas värde.",
-    "health.metric_lower": "Nedre våningens värmeförlust som andel av inställningarnas uppskattning.",
-    "health.metric_tank": "Hur snabbt varmvattentanken svalnar när pumpen står still, i °C per timme. Lägre är bättre isolerat.",
+    "health.metric_lower": "Nedre våningens värmeförlust som andel av inställningarnas uppskattning. Över 100 % förlorar mer; utan mätningar är det inställningarnas uppskattning.",
+    "health.metric_tank": "Hur snabbt varmvattentanken svalnar när pumpen står still, i °C per timme. Lägre är bättre isolerat; utan mätningar är det standardvärdet.",
     "health.metric_cop": "Om värmepumpen fortfarande ger lika mycket värme per kWh som förut. Ett streck betyder att den inte bevakas än.",
-    "health.metric_gains": "Värme från människor, matlagning och apparater per timme, som planen räknar som gratis uppvärmning.",
+    "health.metric_gains": "Värme från människor, matlagning och apparater per timme, i kW, som planen räknar som gratis uppvärmning. Högre staplar är mer gratis värme; utan mätningar räknar planen ingen.",
     "health.debug_title": "Felsökningsinsamling",
     "health.debug_off": "Av. När en felrapport ber om det spelar Starta in en vecka av cykler i diagnostikfilen.",
     "health.debug_active": "Samlar in: {rows} poster hittills, ungefär {days} dagar kvar.",
@@ -9559,11 +9559,17 @@ function healthLearningHtml(plan) {
   return rows.length ? `<div class="health-learning"><h3 class="health-h">${esc(L("health.learning"))}</h3>${rows.join("")}</div>` : "";
 }
 
-/** One learner row: what it is, its evidence in words, its value and a bar.
- * Its hover says what the figure is (`health.metric_<id>`). */
+/** A model row's hover, by the owner's spec: what the figure is in plain
+ * words (`health.metric_<id>`, which also says what no data means), then the
+ * row's current reason -- its learner phase, its evidence or its COP reason. */
+function healthModelTitle(id, reason) {
+  return [L(`health.metric_${id}`), reason].filter(Boolean).join("\n");
+}
+
+/** One learner row: what it is, its evidence in words, its value and a bar. */
 function healthModelRow(id, title, detail, value, share, tone) {
   const pct = Math.round(Math.max(0, Math.min(1, Number(share) || 0)) * 100);
-  return `<div class="health-row model-row" data-model-row="${id}" data-tone="${tone || "ok"}" title="${esc(L(`health.metric_${id}`))}">` +
+  return `<div class="health-row model-row" data-model-row="${id}" data-tone="${tone || "ok"}" title="${esc(healthModelTitle(id, detail))}">` +
     `<span class="adv-text">${esc(title)}<span class="adv-sub">${esc(detail)}</span></span>` +
     `<span class="model-value">${esc(value)}</span>` +
     `<span class="model-bar" aria-hidden="true"><span style="width:${pct}%"></span></span></div>`;
@@ -9586,9 +9592,10 @@ function healthGainsRow(gains, learning) {
   const bars = kw.map((g, h) => `<span class="gains-bar" title="${String(h).padStart(2, "0")}:00" ` +
     `style="height:${top > 0 ? Math.max(4, Math.round((g / top) * 100)) : 4}%"></span>`).join("");
   const peak = L("health.model_gains_peak", { kw: top.toFixed(1), hh: String(at).padStart(2, "0") });
-  return `<div class="health-row model-row" data-model-row="gains" data-tone="ok" title="${esc(L("health.metric_gains"))}">` +
+  const detail = learning ? `${learning.text} ${peak}` : peak;
+  return `<div class="health-row model-row" data-model-row="gains" data-tone="ok" title="${esc(healthModelTitle("gains", detail))}">` +
     `<span class="adv-text">${esc(L("health.model_gains"))}<span class="adv-sub">` +
-    `${esc(learning ? `${learning.text} ${peak}` : peak)}</span></span>` +
+    `${esc(detail)}</span></span>` +
     `<span class="gains-strip" aria-hidden="true">${bars}</span></div>`;
 }
 
diff --git a/dev/programme/delivery/2997.md b/dev/programme/delivery/2997.md
new file mode 100644
index 000000000..9b2ba9f3c
--- /dev/null
+++ b/dev/programme/delivery/2997.md
@@ -0,0 +1 @@
+- [#2997](https://github.com/tvofi/heatpump_optimizer/pull/2997) — **open**, R10-UX-HEALTH part 2: residual carries (R10-UX-HEALTH)
diff --git a/tests/card.mjs b/tests/card.mjs
index 7519d6878..896035599 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -12195,6 +12195,42 @@ check("without an indoor reading the corner now label is absent",
       /Waiting: it learns when it is cold enough outside/.test(waiting) && !/colder/.test(waiting), waiting);
     check("UX-HEALTH D: a learner that is off has no row",
       !/data-model-row="gains"/.test(modelOf(metered({ learner_progress: { gains: { phase: "off", samples: 0 } } }))));
+    // The owner's hover spec (carry 14): every score and scale hover says what
+    // its figure is in plain words, what no data means, and the row's current
+    // reason. Driven on an install with no samples anywhere, in both languages,
+    // over every model row the page draws -- a row added without the hover's
+    // two parts fails here, not only the six named today.
+    {
+      const bare = modelStates({
+        heat_loss: { scale: 1.0, samples: 0, learned: false },
+        lower_floor: { ratio: 1.0, samples: 0, learned: false },
+        solar_aperture: { scale: 1.0, samples: 0, needed: 30 },
+        tank_cooling: { rate_c_per_h: 0.9, samples: 0, learned: false },
+        cop: { scale: 1.0, samples: 0, alarm: false, watched_buckets: 0 },
+        internal_gains_kw: Array(24).fill(0.1),
+        learner_progress: {
+          house: { phase: "waiting", waiting_for: "colder", samples: 0 },
+          lower: { phase: "waiting", waiting_for: "colder", samples: 0 },
+          solar: { phase: "waiting", waiting_for: "sunnier", samples: 0 },
+          gains: { phase: "waiting", waiting_for: "colder", samples: 0 },
+        },
+      });
+      const esc = fn("esc");
+      for (const [lang, noData] of [["en", /with no samples|dash means/], ["sv", /utan mätningar|streck betyder/]]) {
+        const m = modelOf(bare, lang);
+        const strings = fn("STRINGS")[lang];
+        const ids = [...m.matchAll(/data-model-row="([^"]+)"/g)].map((x) => x[1]);
+        const bad = ids.filter((id) => {
+          const title = (new RegExp(`data-model-row="${id}"[^>]*title="([^"]*)"`).exec(m) || [])[1] || "";
+          const reason = (/<span class="adv-sub">([^<]*)</.exec(rowOf(m, id)) || [])[1] || "";
+          const metric = strings[`health.metric_${id}`];
+          return !metric || !title.includes(esc(metric)) || !noData.test(metric)
+            || !reason || !title.includes(reason);
+        });
+        check(`hover spec (${lang}): every model row's hover says what it measures, what no data means and its current reason`,
+          ids.length === 6 && bad.length === 0, `rows ${ids.join(",")}; lacking ${bad.join(",")}`);
+      }
+    }
     const nometer = rowOf(modelOf(unmetered), "heat_loss");
     check("UX-HEALTH D: with no power meter the heat loss is not called learned",
       /Not observable without a power meter/.test(nometer) && !/Learned from/.test(nometer), nometer);
@@ -12362,6 +12398,30 @@ check("without an indoor reading the corner now label is absent",
   check("placeLabel names a known place and keeps an unknown id as itself",
     fn("placeLabel")("wood_tank") === fn("STRINGS").en["places.wood_tank"] && fn("placeLabel")("garage_loop") === "garage_loop",
     `${fn("placeLabel")("wood_tank")} / ${fn("placeLabel")("garage_loop")}`);
+  // P08/P41, through a real render: the Setup boxes are a literal list in
+  // the card, every one of them in SETUP_CONFIGURE_PAGE today, so no topology
+  // reaches the layout code's fallback. A box added without its page is the
+  // case it guards: withdraw one place's page for the render, and its
+  // Configure chip names the place -- the fallback the direct placeLabel call
+  // above never reaches -- rather than reading undefined.
+  {
+    const map = fn("SETUP_CONFIGURE_PAGE");
+    const held = map.wood_tank;
+    delete map.wood_tank;
+    let card;
+    try { card = mkSetup(); } finally { map.wood_tank = held; }
+    const box = setupBox(card, "wood_tank");
+    const html = collect(card.shadowRoot).join("\n");
+    const pages = [...html.matchAll(/<text class="setup-chip-page"[^>]*>([\s\S]*?)<\/text>/g)]
+      .map((m) => [...m[1].matchAll(/<tspan[^>]*>([^<]*)<\/tspan>/g)].map((t) => t[1]).join(" "));
+    const aria = [...html.matchAll(/class="setup-chip-hit"[^>]*?aria-label="([^"]*)"/g)].map((m) => m[1]);
+    const name = fn("placeLabel")("wood_tank");
+    check("P08/P41: the Configure chip of a place with no options page names the place, never undefined",
+      held && box && name !== "wood_tank" && pages.includes(name)
+      && aria.some((t) => t.includes(name))
+      && !pages.concat(aria).some((t) => /undefined/.test(t)),
+      `box ${box ? "drawn" : "missing"}; pages ${JSON.stringify(pages)}`);
+  }
 
   // The other four tabs still render.
   for (const [page_, marker] of [["plan", /stat-row|tile/], ["setup", /setup-page/],
@@ -13061,6 +13121,17 @@ check("without an indoor reading the corner now label is absent",
     && viaMouse.setup.pickerKey === "heat_pump_power_entity"
     && viaMouse.setup.pickerFocus === false && viaMouse.setup.pickerViaKeyboard === false,
     `keys ${viaKeys.setup.pickerFocus}/${viaKeys.setup.pickerViaKeyboard} mouse ${viaMouse.setup.pickerFocus}/${viaMouse.setup.pickerViaKeyboard}`);
+  // P08/P41: and the opened picker is drawn -- the state above changes
+  // nothing on screen until a render follows it.
+  {
+    const host = open("advisor");
+    const renders = [];
+    const real = host._render.bind(host);
+    host._render = () => { renders.push(host.dialog.page); return real(); };
+    openSetupSlot(host, "heat_pump_power_entity", { detail: 1 });
+    check("openSetupSlot renders the page it opens",
+      renders[renders.length - 1] === "setup", `renders on ${JSON.stringify(renders)}`);
+  }
 
   // openHaLink resolves this card's entry through the registry and follows
   // haLink with it; a failed lookup links the whole integration. Driven
diff --git a/tests/debug_collect.py b/tests/debug_collect.py
index b7ce7efef..4ab4f1a8b 100644
--- a/tests/debug_collect.py
+++ b/tests/debug_collect.py
@@ -367,10 +367,24 @@ R.check(
     and lit == {}
     and available is True
     and held_collector.final
-    and button.available is False
-    and button.extra_state_attributes == {"waiting_for": "debug_collect"},
+    and button.available is False,
     f"dark={dark} lit={lit} available={available} final={held_collector.final}",
 )
+# #2809: a finished collection with the option on is dark for another reason
+# than the option-off case -- it waits for the action's start, not the option
+# it already has. Perturbation: the same collector not final names nothing.
+final_reason = button.extra_state_attributes
+held_collector.final = False
+open_reason = button.extra_state_attributes
+held_collector.final = True
+R.check(
+    "the finalize button on a finished collection names the action's start, "
+    "not the option that is already on",
+    final_reason == {"waiting_for": "debug_collect_start"}
+    and final_reason != dark
+    and open_reason == {},
+    f"final={final_reason} open={open_reason} off={dark}",
+)
 
 
 # -- a scalar domain is one value, not a container walked in its place --------
diff --git a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.BOOLOP.85c924c9.json b/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.BOOLOP.85c924c9.json
deleted file mode 100644
index 9d0c8f315..000000000
--- a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.BOOLOP.85c924c9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/button.py:DebugFinalizeButton.extra_state_attributes BOOLOP 85c924c9",
-  "killed_by": "tests/debug_collect.py",
-  "old": "        if collector is not None and not collector.final:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fc76a05577985c92574e4d42433f61192efe47f4: BOOLOP (`if collector is not None or not collector.final:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.GUARD_OFF.85c924c9.json b/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.GUARD_OFF.85c924c9.json
deleted file mode 100644
index f190391ef..000000000
--- a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.GUARD_OFF.85c924c9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/button.py:DebugFinalizeButton.extra_state_attributes GUARD_OFF 85c924c9",
-  "killed_by": "tests/debug_collect.py",
-  "old": "        if collector is not None and not collector.final:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fc76a05577985c92574e4d42433f61192efe47f4: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.RETURN_DEL.3dca65c8.json b/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.RETURN_DEL.3dca65c8.json
deleted file mode 100644
index 266443142..000000000
--- a/tests/mutation_ledger/killed_by/button.py/DebugFinalizeButton.extra_state_attributes.RETURN_DEL.3dca65c8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/button.py:DebugFinalizeButton.extra_state_attributes RETURN_DEL 3dca65c8",
-  "killed_by": "tests/debug_collect.py",
-  "old": "        return {\"waiting_for\": \"debug_collect\"}",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fc76a05577985c92574e4d42433f61192efe47f4: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}

