# per-key step-4 analysis for box D3-g31 (written into results/<key>.json by build_results.py)
F = "custom_components/heatpump_optimizer/price_model.py"
EQ_EPS_INPUTS = ("production: 192 coordinator-shaped calls (n_steps 0,1,4,96,192; step offset 0,37; known lengths 0,1,n-1,n,n+3,n/2 "
                 "with negative prices; models None, fresh, young (2 days), trusted from_dict); direct: step_start_times shorter than "
                 "the horizon or the known run (len 0,1,2), known longer than n_steps")
S = {}
def eq(key, base, mut, inputs, should, note):
    S[key] = dict(cls="equivalent-candidate", base=base, mut=mut, inputs=inputs, should_fail=should, note=note)
def cand(key, base, mut, inputs, should, finding):
    S[key] = dict(cls="candidate", base=base, mut=mut, inputs=inputs, should_fail=should, finding=finding)

QF_IN = ("from_dict-loaded models, quarter factor in {0.25,0.5,1.0,1.3,4.0,nan,inf,-1,0} x quarter_days {0,1,3,5,9} at 20 instants "
         "(weekday and weekend, every quarter mark); direct-constructed factors nan, inf, -inf, 1.3, 0.25 at trust 0")
QF_NOTE = ("At trust 0 the mutant returns 1 + (f - 1) * 0 == 1.0 for every finite factor; only a non-finite stored factor "
           "separates, and from_dict's _stored_rows rejects non-finite bins and _in_domain clips the rest to [0.25, 4.0], "
           "while the learner writes clipped finite factors. Equivalent through every load and learn path.")
eq("ba9f6b92f678ab10", "prod_differ=0 of 900; direct nan factor at trust 0 -> 1.0", "prod_differ=0 of 900; direct nan factor at trust 0 -> nan", QF_IN,
   "none through production; a direct unit call of quarter_factor on a constructed model with a non-finite factor at quarter_days 0 asserting 1.0 would", QF_NOTE)
eq("c9f07b68ade152e6", "prod_differ=0 of 900; direct nan factor at trust 0 -> 1.0", "prod_differ=0 of 900; direct nan factor at trust 0 -> nan", QF_IN,
   "none through production (trust = min(1, quarter_days/5) with quarter_days floored at 0 is never negative); only the direct non-finite-factor call separates", QF_NOTE)
SG_IN = ("from_dict-loaded models, residual_var in {0,-0.0,1e-12,0.04,-0.01,-5} x days {0,1,5,9} x level {0,-0,0.5,2,-0.3,1e-300,1e300} "
         "at 5 instants; direct-constructed var -1e-3, var 0 with level inf/nan, var -0.0 with level inf")
SG_NOTE = ("from_dict floors residual_var at 0 (and the learner's EWMA of squares is >= 0), and extend_price_series passes a finite level "
           "(finite known prices over a shape mean > 1e-6), so var < 0 and a non-finite level never reach sigma; at var == 0 with a "
           "finite level the mutant's level*sqrt(0)*conf is 0.0 (or -0.0, equal). Equivalent through production.")
eq("45cd5752f930a064", "prod_differ=0 of 840; direct var -1e-3 -> 0.0", "prod_differ=0 of 840; direct var -1e-3 -> nan", SG_IN,
   "none through production; a direct sigma call with a negative variance or a non-finite level asserting 0.0 would", SG_NOTE)
eq("e72d16a241bfa7be", "prod_differ=0 of 840; direct var 0, level inf -> 0.0", "prod_differ=0 of 840; direct var 0, level inf -> nan", SG_IN,
   "none through production; a direct sigma call at var 0 with a non-finite level asserting 0.0 would", SG_NOTE)

def summ(key, line, field, base, mut):
    cand(key, f"{field} max={base} (24 of 24 bins non-zero after 28 observed days)", f"{field} max=0.0 (24 of 24 bins zero)",
         "28 days folded by observe_day (seeded rng 11, Mon 2026-01-05..); null: a fresh model (residual_var 0)",
         f"tests/features.py, which drives the coordinator's _grid_view (price_prior: PriceShapeModel.summary()) on the traced baseline "
         f"(carried full-net scripts_ran), lacks an assertion that price_prior.{field} equals sqrt(residual_var) after observed days; "
         f"no check in tests/ names {field} at all (grep count 0)",
         dict(title=f"No check pins price_prior.{field} against the learned residual variance; zeroing it is unseen",
              claim=f"Replacing price_model.py:{line} sqrt(max(0, v)) by sqrt(0) in PriceShapeModel.summary publishes an all-zero "
                    f"{field} after 28 learned days ({base} -> 0.0) and the full GATE_SCOPE=full GOLDEN_MODE=drift gate stays green",
              severity="medium",
              metric_definition=f"max over the 24 bins of PriceShapeModel.summary()['{field}'] after 28 observe_day folds (seeded)",
              perturbation=dict(change=f"price_model.py:{line} `round(float(np.sqrt(max(0.0, v))), 4)` -> `round(float(np.sqrt((0.0))), 4)`",
                                expected_direction="to_zero", observed_value=0.0),
              null_control=dict(command="the same probe's fresh-model arm", value="null_bins_differ=0",
                                note="a model with residual_var 0 publishes zeros in both arms"),
              phenomenon_property="The published price prior's per-hour sigma equals the square root of the learned residual variance",
              files=[F], proposed_fix_scope=f"tests/features.py: one check folding days and asserting summary()['{field}'] == round(sqrt(residual_var), 4)"))
summ("3a064c11321daba7", 417, "weekday_sigma", 0.538, 0.0)
summ("efa02472a5a773bc", 421, "weekend_sigma", 0.4726, 0.0)

eq("6743e8b3d654cd32", "ingress: (1,0) learned for a quarter day with one nan quarter; direct: (1,0)",
   "ingress: (1,0); direct: (0,0) (the nan quarter makes its hour mean nan and observe_day rejects the day)",
   "quarter-resolution day with a nan / inf / -inf quarter, an hourly day with a nan hour, an all-finite quarter day; each fed raw "
   "and through prices_from_tibber_payload; apply_price_adjustments on a nan total",
   "none through production: both ingress paths (prices_from_tibber_payload via _raw_value/finite_float, apply_price_adjustments) "
   "drop non-finite totals before self._prices, the only list PriceShapeLearner.fold reads; a direct fold of raw rows separates",
   "Defence in depth behind the ingress filters (#2236): 0 of 5 cases move through ingress (nonfinite rows after Tibber and entity "
   "ingress: 0 and 0); 3 of 5 move on raw rows (days learned 1 -> 0). Equivalent through production.")

cand("a38612ad3ad9cd34", "all-zero persisted weekday shape restored as all 1.0 (one warning); guessed 17:00 price at level 1.0 = 1.0",
     "restored as all 0.0 (no warning); guessed 17:00 price = 0.0",
     "persisted weekday shapes: all zero, one zero bin, a negative bin, exactly at the guard's bound, nextafter above/below it, "
     "flat ones, the learner's cone edge [0.2]*23+[3.0]",
     "tests/features.py and tests/finite_boundary.py (carried should_have_failed; both restore PriceShapeModel via from_dict on the "
     "traced baseline) lack a restore of an all-zero persisted shape asserting the D1-s5-02 clip (shape renormalised to 1.0, a "
     "warning); tests/entities.py:42270 only counts _in_domain's call sites",
     dict(title="No check restores an all-zero persisted price shape; letting _in_domain accept low == 0 is unseen",
          claim="With price_model.py:141 `low > 0.0` -> `low >= 0.0`, PriceShapeModel.from_dict keeps an all-zero persisted shape "
                "(max |shape delta| 1.0, warning count 1 -> 0) so every guessed price past the published horizon is 0.0 instead of "
                "the level, and the full gate stays green",
          severity="low",
          metric_definition="max |restored shape - mutant restored shape| for a persisted all-zero weekday shape, and predict(Wed 17:00, level 1.0)",
          perturbation=dict(change="price_model.py:141 `if low > 0.0 and ...` -> `if low >= 0.0 and ...`", expected_direction="to_zero", observed_value=0.0),
          null_control=dict(command="the same probe's flat-ones and learner-cone-edge cases", value="max_abs_shape_delta=0",
                            note="profiles the learner can write are identical in both arms"),
          phenomenon_property="A persisted price profile with a non-positive bin is never adopted unclipped",
          files=[F], proposed_fix_scope="tests/features.py: from_dict of an all-zero shape asserting the renormalised shape and a warning"))
cand("f06caefa38815e4f", "profile [0.5]*23+[bound] restored unchanged, 0 warnings; guessed 17:00 price at level 1.0 = 0.5",
     "clipped and renormalised (max |delta| 2.53448), 1 warning; guessed 17:00 price = 0.827586",
     "persisted weekday shapes: all zero, one zero bin, a negative bin, exactly at the guard's bound, nextafter above/below it, "
     "flat ones, the learner's cone edge [0.2]*23+[3.0]",
     "tests/features.py and tests/finite_boundary.py (restore PriceShapeModel via from_dict on the traced baseline) lack a restore of "
     "a profile whose max/min ratio sits exactly at the guard's bound asserting it is returned unchanged and unwarned",
     dict(title="No check restores a price profile exactly at _in_domain's ratio bound; <= -> < there is unseen",
          claim="With price_model.py:141 `high <= bound` -> `high < bound`, PriceShapeModel.from_dict clips and renormalises a "
                "persisted profile whose max sits exactly at low*(hi/lo)*(1+1e-9) (max |delta| 2.53448, warnings 0 -> 1) and the full gate stays green",
          severity="low",
          metric_definition="max |restored shape delta| and warning count for a persisted shape [0.5]*23+[0.5*(3.0/0.2)*(1+1e-9)]",
          perturbation=dict(change="price_model.py:141 `high <= low * (hi / lo) * (1.0 + 1e-9)` -> `high < ...`", expected_direction="up", observed_value=2.53448),
          null_control=dict(command="the same probe's nextafter-below, flat and cone-edge cases", value="max_abs_shape_delta=0",
                            note="one ulp below the bound both arms keep the profile"),
          phenomenon_property="A persisted profile inside the learner's cone, its bound included, is adopted unchanged",
          files=[F], proposed_fix_scope="tests/features.py: from_dict at the exact bound asserting no clip and no warning"))
cand("28de20de50a9540b", "weekend days 2, weekday days 5 after one Mon..Sun week; Saturday 03:00 guessed price at level 1.0 = 0.737143",
     "weekend days 1, weekday days 6; Saturday 03:00 guessed price = 0.564779",
     "one week of hourly rows Mon 2026-01-05..Sun 01-11 folded by PriceShapeLearner.fold with distinct weekday/weekend shapes; "
     "null: Mon-Fri and Sunday profile indices",
     "tests/features.py, which folds price days through PriceShapeLearner on the traced baseline, lacks a check folding a Saturday "
     "and asserting it lands in PROFILE_WEEKEND (no check in tests/ names _profile_index or PROFILE_WEEKEND; grep count 0)",
     dict(title="No check folds a Saturday into the weekend price profile; Saturday as a weekday is unseen",
          claim="With price_model.py:155 `weekday() >= 5` -> `> 5`, one folded week learns 1 weekend day instead of 2 and the "
                "Saturday 03:00 guessed price at level 1.0 moves 0.737143 -> 0.564779, and the full gate stays green",
          severity="medium",
          metric_definition="model.days[PROFILE_WEEKEND] after folding one Mon..Sun week, and predict(Sat 03:00, level 1.0)",
          perturbation=dict(change="price_model.py:155 `when.weekday() >= 5` -> `when.weekday() > 5`", expected_direction="down", observed_value=1),
          null_control=dict(command="the same probe's Mon-Fri/Sunday index comparison", value="null_days_differ=0",
                            note="only Saturday changes profile"),
          phenomenon_property="Saturday and Sunday are learned and predicted on the weekend profile",
          files=[F], proposed_fix_scope="tests/features.py: fold a week and assert days per profile and a Saturday prediction"))
cand("e5eea05f4463602e", "401/403 text/html body -> verdict reauth; 502 text/html -> fail",
     "401/403/502 text/html -> aiohttp.ContentTypeError raised out of pull_prices (the coordinator catches it as an ordinary ClientError fetch failure, no reauth)",
     "fake aiohttp session: 401, 403, 502 with a text/html body (resp.json() raises ContentTypeError), 500 and 401 with JSON error bodies, 200 with no homes",
     "tests/features.py's 'a refused token asks for REAUTH while a broken API is an ordinary failure' (_g8_pull) replaces _tibber_post "
     "with a scripted stub, so no check drives the real _tibber_post with a non-200 response; it lacks a case whose resp.json() raises",
     dict(title="No check drives _tibber_post with a non-200 reply; reading its body anyway loses reauth on a non-JSON 401",
          claim="With price_model.py:844 `if resp.status != 200:` -> `if False:`, pull_prices raises ContentTypeError instead of "
                "returning reauth for a 401/403 whose body is not JSON (3 of 6 reply shapes move), and the full gate stays green",
          severity="medium",
          metric_definition="pull_prices' verdict per scripted Tibber reply (status, body) through the real _tibber_post",
          perturbation=dict(change="price_model.py:844 `if resp.status != 200:` -> `if False:`", expected_direction="sign_flip", observed_value="raised:ContentTypeError"),
          null_control=dict(command="the same probe's JSON-bodied 401/500 and 200 cases", value="identical verdicts",
                            note="a JSON error body parses in both arms"),
          phenomenon_property="A non-200 Tibber reply is classified by its status alone, never by parsing its body",
          files=[F], proposed_fix_scope="tests/features.py: a fake session reply with status 401 and a non-JSON body asserting ('reauth', ...)"))
for k, base, mut, should in [
    ("3ceb6a076659004f", "prod_differ=0 of 192; direct_differ=0 of 6", "identical", "none: with known_count >= n_steps the general path computes the same level and its fill loop is empty"),
    ("b434193b049a41c3", "prod_differ=0 of 192; direct_differ=0 of 6", "identical", "none: at known_count == n_steps the general path's fill loop is empty and returns the same arrays"),
    ("29db99dee6a5debd", "prod_differ=0 of 192; direct short step_start_times (len 1 < known 3 < n 5) -> prices", "prod identical; direct -> IndexError",
     "none through production (coordinator._price_series passes len(step_starts) == n_steps > known_count); a direct extend_price_series call with fewer step_start_times than known prices would"),
    ("c1e06ebefdc5abad", "prod_differ=0 of 192; direct short step_start_times (len 2 < n 4) -> last start reused", "prod identical; direct -> IndexError (2 of 6)",
     "none through production (i < n_steps == len(step_starts)); a direct call with a horizon longer than step_start_times would"),
    ("886591ca08e1d27e", "prod_differ=0 of 192; direct shape mean exactly 1e-6 -> tail 0.0", "prod identical; direct -> tail 0.45",
     "none through production (shape_for >= SHAPE_MIN 0.2: from_dict and the learner clip shapes to [0.2, 3.0]); only a model reading exactly 1e-6 separates")]:
    eq(k, base, mut, EQ_EPS_INPUTS + ("; plus a model whose shape_for is exactly 1e-6" if k.startswith("886") else ""), should,
       "Equivalent through the coordinator's call shape: " + should)
