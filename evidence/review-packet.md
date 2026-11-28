# Review packet #3945
head: 92e3712af8e5ca935f5a404539c402b403fe7aa9
base: a59a1b0d9ac782fabbe01eb84f4d4ff5a17aee43

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=141071003613 success
arch-score / arch-score id=141070760306 success
arm id=141070460543 skipped
budget-raise-gate / budget-raise-gate id=141070760354 success
cancel-superseded id=141070469720 success
codeql id=141070761712 skipped
codeql / Analyze (actions) id=141070752656 success
codeql / Analyze (javascript-typescript) id=141070752610 success
codeql / Analyze (python) id=141070752608 success
gate id=141071338884 failure
governance id=141070761724 skipped
governance / env-matrix id=141070752749 success
governance / instrument-self-tests id=141070752708 success
governance / policy-docs id=141070752795 success
governance / record id=141070754733 skipped
governance / wave-script id=141070752700 success
hassfest id=141070762233 skipped
hassfest / hassfest id=141070752641 success
kernel-points id=141070761568 skipped
pr-contract id=141071340344 skipped
prelude id=141070469996 success
sweep-self id=141071575356 skipped
tests id=141070762067 skipped
tests / arch-instrument id=141070987265 success
tests / briefs id=141070752681 success
tests / browser id=141070987216 success
tests / claims-autofix id=141075430838 success
tests / closure-scope id=141070752690 success
tests / closures id=141070987271 in_progress
tests / coverage id=141070987228 in_progress
tests / fast (3.14, 1/4) id=141070987221 failure
tests / fast (3.14, 2/4) id=141070987367 success
tests / fast (3.14, 3/4) id=141070987234 success
tests / fast (3.14, 4/4) id=141070987258 success
tests / mutation id=141070752607 success
tests / mutation-autofix id=141071078327 skipped
tests / mutation-pins id=141071078267 skipped
tests / nightly-ha id=141070988556 skipped
tests / nightly-status id=141070752631 failure
tests / replay id=141070989456 skipped
tests / typing id=141070987256 success
validate id=141070761963 skipped
validate / validate-hacs id=141070752546 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 92e3712af8e5ca935f5a404539c402b403fe7aa9 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 7 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/presets.py b/custom_components/heatpump_optimizer/presets.py
index 664ea58322..78d49b8b9d 100644
--- a/custom_components/heatpump_optimizer/presets.py
+++ b/custom_components/heatpump_optimizer/presets.py
@@ -8,9 +8,10 @@ other house started from a wrong prior, and the learners then spent weeks
 walking away from it, rate-limited by guard thresholds that exist precisely
 because the prior might be bad.
 
-This module replaces two unanswerable questions with three answerable ones:
-what the building is made of, roughly when it was built, and what the heat is
-emitted through. Those map onto physics that is well characterised, especially
+This module replaces two unanswerable questions with answerable ones -- the
+questions ``preset_from_config`` reads: what the building is made of, what it
+stands on, roughly when it was built, how much of it is heated, and what the
+heat is emitted through on each floor. Those map onto physics that is well characterised, especially
 for Swedish era bands, which track the insulation standards of their time
 fairly closely.
 
diff --git a/custom_components/heatpump_optimizer/setpoint_check.py b/custom_components/heatpump_optimizer/setpoint_check.py
index 108b478f43..831d04efe9 100644
--- a/custom_components/heatpump_optimizer/setpoint_check.py
+++ b/custom_components/heatpump_optimizer/setpoint_check.py
@@ -3,7 +3,9 @@
 Consistency only — not an optimality advisory. The scoping judge refused
 Fix-to-argmin: the argmin moves 50→65 °C under a price roll and the cost
 surface's deterministic non-convexities (4.2080 SEK/day) exceed the median
-gain (2.72). Space set-point is never recommended.
+gain (2.72). The space set-point is only checked for readability here: under
+Control the pump-duty arbiter writes the plan's own value to it each step
+(``pump_arbiter``), so there is no configured space value to compare.
 """
 from __future__ import annotations
 
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 7fb5a3192e..f2892e79de 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -3492,7 +3492,8 @@ class ThermalModel:
         h_eff = h_base * (1 + wind_sensitivity * wind_speed)
 
         Rain effect: wet building envelope has higher U-value.
-        U_eff = U_wind_adjusted * rain_multiplier (when precipitation > 0)
+        U_eff = U_wind_adjusted * rain_factor: none of the multiplier at
+        0.1 mm/h or less, all of it from 2 mm/h, in proportion between.
         """
         p = self.params
         # The configured coefficient is a nameplate estimate; the learned scale
@@ -3504,9 +3505,7 @@ class ThermalModel:
 
         # Rain effect: apply multiplier when raining
         if precipitation > 0.1:  # threshold for "raining"
-            # Scale rain multiplier based on precipitation intensity
-            # Light rain (0.1-1 mm/h): partial multiplier
-            # Heavy rain (>2 mm/h): full multiplier
+            # Scaled by intensity: the full multiplier from 2 mm/h.
             rain_intensity = min(precipitation / 2.0, 1.0)
             rain_factor = 1.0 + (p.rain_heat_loss_multiplier - 1.0) * rain_intensity
             u_wind *= rain_factor
diff --git a/dev/programme/delivery/3945.md b/dev/programme/delivery/3945.md
new file mode 100644
index 0000000000..dba4316793
--- /dev/null
+++ b/dev/programme/delivery/3945.md
@@ -0,0 +1 @@
+- [#3945](https://github.com/tvofi/heatpump_optimizer/pull/3945) — **open**, R11-PRODUCT-TEXT-PINS: stale product docstrings corrected and the user sentences pinned to the code (R11-PRODUCT-TEXT-PINS)
diff --git a/tests/config_flow_steps.py b/tests/config_flow_steps.py
index f3970065f4..dde0cf2cb1 100644
--- a/tests/config_flow_steps.py
+++ b/tests/config_flow_steps.py
@@ -7496,6 +7496,22 @@ async def config_flow_device_prefill_offer():
         set(shown) == set(suggestions),
         f"{sorted(shown)}",
     )
+    # bb5336e8: the wizard's page posts no after-save choice, its navigation
+    # being always finish_setup, so the second submit's ``self._data.update``
+    # cannot store one. The schema is the null control on the rendered set:
+    # it refuses the key outright, so a stale form posting it is refused
+    # before the step runs.
+    try:
+        preview["data_schema"]({const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE})
+        refused_after_save = False
+    except vol.Invalid:
+        refused_after_save = True
+    check(
+        "device_prefill", "happy",
+        "the wizard's pre-fill page renders no after-save choice and its schema refuses one",
+        const.CONF_AFTER_SAVE not in rendered_keys(preview) and refused_after_save,
+        f"keys={sorted(rendered_keys(preview))} refused={refused_after_save}",
+    )
 
     # What the user keeps lands in the entry's own setup data, and the wizard
     # continues to the menu it would have reached without the offer.
diff --git a/tests/entities.py b/tests/entities.py
index 8911ccba36..cafafa392f 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -28289,6 +28289,173 @@ R.check(
     f"untemplated: {sorted(_reason_values - set(narrative_mod.TEMPLATES['en']))}",
 )
 
+# R11-PRODUCT-TEXT-PINS: three corrected user sentences, each read from the
+# shipped artifact and held to the code that decides what it describes, so
+# reverting the text fails here rather than passing as prose.
+import numpy as _ptp_np  # noqa: E402
+from heatpump_optimizer import coordinator as _ptp_coord_mod  # noqa: E402
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    ThermalModel as _PtpModel,
+    ThermalParameters as _PtpParams,
+)
+
+# (1) The narrative's hot-water sentences (dabc6d30af). The witness plan's
+# dearest step is a hot-water charge outside any window. Its window charge is
+# a later step, not the present one. classify_dhw_steps tags the first
+# dhw_preheat and the second dhw_window. So a dhw_preheat sentence claiming
+# cheap electricity states what the classifier never decided, and so does a
+# dhw_window sentence claiming "now". The vocabulary is per language. The
+# texts the correction replaced are the detector's own control: a detector
+# that missed them would read as a pass.
+_ptp_prices = _ptp_np.array([0.5, 3.0, 0.4])
+_ptp_codes = optimizer_mod.classify_dhw_steps(
+    _ptp_np.array([0.0, 2.0, 2.0]),
+    _ptp_np.array([False, False, True]),
+    _ptp_np.zeros(3),
+    None,
+    3,
+    idle=optimizer_mod.IdleContext(prices=_ptp_prices),
+)
+R.check(
+    "the hot-water witness: the dearest step is dhw_preheat, a later "
+    "in-window step is dhw_window",
+    _ptp_codes[1] == optimizer_mod.REASON_DHW_PREHEAT
+    and int(_ptp_np.argmax(_ptp_prices)) == 1
+    and _ptp_codes[2] == optimizer_mod.REASON_DHW_WINDOW,
+    f"codes={_ptp_codes}",
+)
+_PTP_PRICE_CLAIM = re.compile(r"(cheap|billig|günstig)", re.IGNORECASE)
+_PTP_NOW_CLAIM = re.compile(r"\b(now|nu|jetzt)\b", re.IGNORECASE)
+_ptp_replaced = {
+    "dhw_preheat": (
+        "charging the tank while electricity is cheap: {kwh} kWh ({cost} {currency})",
+        "tanken laddas medan elen är billig: {kwh} kWh ({cost} {currency})",
+        "Speicher laden, solange Strom günstig ist: {kwh} kWh ({cost} {currency})",
+    ),
+    "dhw_window": (
+        "hot water needed now: {kwh} kWh ({cost} {currency})",
+        "varmvatten behövs nu: {kwh} kWh ({cost} {currency})",
+        "Warmwasser jetzt benötigt: {kwh} kWh ({cost} {currency})",
+    ),
+}
+_ptp_claim = {"dhw_preheat": _PTP_PRICE_CLAIM, "dhw_window": _PTP_NOW_CLAIM}
+R.check(
+    "the hot-water claim detector reads every replaced sentence as a claim",
+    all(_ptp_claim[k].search(s) for k, ss in _ptp_replaced.items() for s in ss),
+    repr({k: [bool(_ptp_claim[k].search(s)) for s in ss] for k, ss in _ptp_replaced.items()}),
+)
+_ptp_claiming = sorted(
+    f"{lang}.{key}"
+    for lang, table in narrative_mod.TEMPLATES.items()
+    for key, rx in _ptp_claim.items()
+    if rx.search(table[key])
+)
+R.check(
+    "no dhw_preheat sentence claims a price and no dhw_window sentence "
+    "claims the present, in any language",
+    not _ptp_claiming and set(narrative_mod.TEMPLATES) >= {"en", "sv", "de"},
+    f"claiming: {_ptp_claiming}",
+)
+
+# (2) set_thermal_parameters' rain multiplier description names two rain
+# rates: the one from which the whole multiplier applies, then the one at or
+# below which none does. Both are read from every shipped text, in that
+# order, and effective_heat_loss_coefficient is driven at each and between.
+_ptp_texts = {
+    _p.name: json.loads(_p.read_text(encoding="utf-8"))["services"][
+        "set_thermal_parameters"]["fields"]["rain_heat_loss_multiplier"]["description"]
+    for _p in [ROOT / "strings.json", *sorted((ROOT / "translations").glob("*.json"))]
+}
+_ptp_rates = {
+    _n: tuple(float(_m.replace(",", ".")) for _m in re.findall(r"(\d+(?:[.,]\d+)?)\s*mm/h", _t))
+    for _n, _t in _ptp_texts.items()
+}
+_ptp_params = _PtpParams(rain_heat_loss_multiplier=1.15, wind_sensitivity=0.0)
+_ptp_model = _PtpModel(_ptp_params)
+_ptp_dry = _ptp_model.effective_heat_loss_coefficient(0.2, 0.0, 0.0)
+
+
+def _ptp_rain_factor(mm_h):
+    return _ptp_model.effective_heat_loss_coefficient(0.2, 0.0, mm_h) / _ptp_dry
+
+
+def _ptp_rain_agrees(rates):
+    if len(rates) != 2 or not rates[1] < rates[0]:
+        return False
+    full, none = rates
+    extra = _ptp_params.rain_heat_loss_multiplier - 1.0
+    half = (none + full) / 2.0
+    return (
+        abs(_ptp_rain_factor(full) - 1.15) < 1e-12
+        and abs(_ptp_rain_factor(2.0 * full) - 1.15) < 1e-12
+        and _ptp_rain_factor(none) == 1.0
+        and _ptp_rain_factor(none + 1e-6) > 1.0
+        and abs(_ptp_rain_factor(half) - (1.0 + extra * half / full)) < 1e-12
+    )
+
+
+R.check(
+    "every rain-multiplier description states the full and the zero rain "
+    "rate effective_heat_loss_coefficient applies, in proportion between",
+    len(_ptp_texts) >= 4 and all(_ptp_rain_agrees(r) for r in _ptp_rates.values()),
+    f"rates={_ptp_rates}",
+)
+R.check(
+    "the rain-rate check refuses a text that names other rates",
+    not _ptp_rain_agrees((1.0, 0.1)) and not _ptp_rain_agrees((2.0, 0.0))
+    and not _ptp_rain_agrees(()),
+)
+
+# (3) run_optimization's no-prices error says how many price steps the solve
+# needs. The number is read from the shipped English message and the
+# coordinator's own run is driven on a horizon cut one step short of it and
+# at it: short answers no_prices, at it does not. That the service handler
+# maps no_prices to this message is features.py's "run_optimization on a
+# stale list raises the same no-prices error".
+_PTP_WORDS = dict(zip(
+    ("two", "three", "four", "five", "six", "seven", "eight"), range(2, 9)))
+_ptp_msg = json.loads((ROOT / "strings.json").read_text(encoding="utf-8"))[
+    "exceptions"]["run_optimization_no_prices"]["message"]
+_ptp_word = re.search(r"fewer than (\w+) electricity price steps", _ptp_msg)
+_ptp_need = _PTP_WORDS.get(_ptp_word.group(1)) if _ptp_word else None
+
+
+def _ptp_run_on(steps):
+    _h, _e, coord = _d801_coordinator(_FLOW_CONFIG)
+    # Prices from this hour on, so the uncut horizon covers now; its length
+    # is the check's own precondition, read back below.
+    start = dt_util.now().replace(minute=0, second=0, microsecond=0)
+    coord._prices = [
+        {**row, "starts_at": (start + timedelta(hours=h)).isoformat()}
+        for h, row in enumerate(coord._prices)
+    ]
+    real = coord._forecast_arrays
+    _ptp_full.append(len(real().prices))
+
+    def cut(now=None):
+        return _ptp_coord_mod.ForecastArrays(*(a[:steps] for a in real(now)))
+
+    coord._forecast_arrays = cut
+    try:
+        return asyncio.run(coord.async_run_optimization())
+    except Exception as err:  # noqa: BLE001 -- the check reads only "not no_prices"
+        return f"raised {type(err).__name__}"
+
+
+_ptp_full = []
+_ptp_runs = (
+    {n: _ptp_run_on(n) for n in (_ptp_need - 1, _ptp_need)} if _ptp_need else {}
+)
+R.check(
+    "the no-prices message's step count is the run's own minimum: one step "
+    "short answers no_prices, that many does not",
+    bool(_ptp_runs)
+    and min(_ptp_full) > _ptp_need
+    and _ptp_runs[_ptp_need - 1] == "no_prices"
+    and _ptp_runs[_ptp_need] != "no_prices",
+    f"need={_ptp_need} uncut={_ptp_full} runs={_ptp_runs} message={_ptp_msg!r}",
+)
+
 # Home Assistant looks a state translation up by the state string itself, so
 # every option has to be a legal translation key. script/hassfest's
 # RE_TRANSLATION_KEY, transcribed from 2025.2.0: lowercase alphanumeric with
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 6363b1e4b1..bbdfb45149 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17191,
+ "class_excess_loc": 17190,
  "const_modules_over_50": 4,
  "coordinator_attrs": 133,
  "coordinator_multiassigned_attrs": 100,
@@ -16,9 +16,9 @@
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
- "module_excess_loc": 21598,
+ "module_excess_loc": 21597,
  "name_kept_members": 38,
- "recorded_at": "e84856520dc4de8d70b68d67a206c6f2278351ad",
+ "recorded_at": "ac9045c223721608e684c8a2213831aa34c1fa4f",
  "seam_cut_total": 413,
  "unloaded_package_imports": 0
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
