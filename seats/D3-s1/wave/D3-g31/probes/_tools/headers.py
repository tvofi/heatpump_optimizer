import json, sys, re
from pathlib import Path
W = Path(sys.argv[1]); SP = Path(sys.argv[2])
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes"
MACH = "box D3-g31 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14)"
H = {
"ba9f6b92f678ab10": dict(sym="price_model:PriceShapeModel.quarter_factor", line=303, pert="`if trust <= 0.0:` -> `if False:`",
  metric="calls of PriceShapeModel.quarter_factor whose value differs baseline vs mutant, over models loaded by from_dict (production domain)",
  exp=["prod_differ=0 count (of 900)", "null_differ=0 count", "direct_factor_nan_trust0 baseline=1.0 mutant=nan (outside from_dict's domain: _stored_rows rejects non-finite bins)"],
  direction="none in production; 1.0 -> nan only for a non-finite factor no load path can deliver", null="trust 1 (quarter_days 5), factor 1.3: identical both arms"),
"c9f07b68ade152e6": dict(sym="price_model:PriceShapeModel.quarter_factor", line=303, pert="`if trust <= 0.0:` -> `if trust < 0.0:`",
  metric="calls of PriceShapeModel.quarter_factor whose value differs baseline vs mutant, over models loaded by from_dict (production domain)",
  exp=["prod_differ=0 count (of 900)", "null_differ=0 count", "direct_factor_nan_trust0 baseline=1.0 mutant=nan (outside from_dict's domain)"],
  direction="none in production; at trust == 0 the mutant computes 1 + (f - 1) * 0 == 1.0 for every finite f", null="trust 1, factor 1.3"),
"45cd5752f930a064": dict(sym="price_model:PriceShapeModel.sigma", line=357, pert="`if var <= 0.0:` -> `if False:`",
  metric="calls of PriceShapeModel.sigma whose value differs baseline vs mutant, over from_dict models and finite levels (production domain)",
  exp=["prod_differ=0 count (of 840)", "null_differ=0 count", "direct_var-1e-3_level0.5 baseline=0.0 mutant=nan", "direct_var0_level_inf baseline=0.0 mutant=nan"],
  direction="none in production (from_dict floors var at 0, extend_price_series passes a finite level); 0.0 -> nan off-domain", null="var 0.04, trust 1"),
"e72d16a241bfa7be": dict(sym="price_model:PriceShapeModel.sigma", line=357, pert="`if var <= 0.0:` -> `if var < 0.0:`",
  metric="calls of PriceShapeModel.sigma whose value differs baseline vs mutant, over from_dict models and finite levels (production domain)",
  exp=["prod_differ=0 count (of 840)", "null_differ=0 count", "direct_var0_level_inf baseline=0.0 mutant=nan"],
  direction="none in production; at var == 0 the mutant returns level*0*conf == 0.0 for finite level", null="var 0.04, trust 1"),
"3a064c11321daba7": dict(sym="price_model:PriceShapeModel.summary", line=417, pert="`round(float(np.sqrt(max(0.0, v))), 4)` (weekday_sigma) -> `round(float(np.sqrt((0.0))), 4)`",
  metric="max over 24 bins of PriceShapeModel.summary()['weekday_sigma'] after 28 observed days (published as GridView.price_prior)",
  exp=["weekday_sigma_max_baseline=0.538", "weekday_sigma_max_mutant=0.0", "weekday_sigma_bins_differ=24 count", "null_bins_differ=0 count"],
  direction="to_zero", null="a fresh model (residual_var 0): both arms all zeros"),
"efa02472a5a773bc": dict(sym="price_model:PriceShapeModel.summary", line=421, pert="`round(float(np.sqrt(max(0.0, v))), 4)` (weekend_sigma) -> `round(float(np.sqrt((0.0))), 4)`",
  metric="max over 24 bins of PriceShapeModel.summary()['weekend_sigma'] after 28 observed days (published as GridView.price_prior)",
  exp=["weekend_sigma_max_baseline=0.4726", "weekend_sigma_max_mutant=0.0", "weekend_sigma_bins_differ=24 count", "null_bins_differ=0 count"],
  direction="to_zero", null="a fresh model (residual_var 0): both arms all zeros"),
"6743e8b3d654cd32": dict(sym="price_model:_entries_by_day (via hourly_from_entries -> PriceShapeLearner.fold)", line=586, pert="`if not np.isfinite(value):` -> `if False:`",
  metric="(weekday days, weekday quarter days) learned by one PriceShapeLearner.fold, rows as pull_prices' ingress delivers them vs raw",
  exp=["ingress_cases_differ=0 count (of 5)", "direct_cases_differ=3 count (of 5): a non-finite quarter makes the hour mean nan and the day is not learned (1 -> 0)", "nonfinite_rows_after_tibber_ingress=0", "nonfinite_rows_after_entity_ingress=0"],
  direction="none through ingress; days learned 1 -> 0 on raw rows only", null="an all-finite quarter day: (1,1) both arms"),
"a38612ad3ad9cd34": dict(sym="price_model:_in_domain (via PriceShapeModel.from_dict)", line=141, pert="`low > 0.0` -> `low >= 0.0`",
  metric="max |shape delta| after PriceShapeModel.from_dict of a persisted weekday shape, and the guessed 17:00 price at level 1.0",
  exp=["all_zero max_abs_shape_delta=1 warnings baseline=1 mutant=0 tail_price_17h baseline=1 mutant=0", "cases_moved=1 count (of 8)"],
  direction="to_zero (an all-zero persisted shape is kept and prices the guessed tail at 0)", null="flat ones, the learner's cone edge [0.2]*23+[3.0]: identical"),
"f06caefa38815e4f": dict(sym="price_model:_in_domain (via PriceShapeModel.from_dict)", line=141, pert="`high <= bound` -> `high < bound`",
  metric="max |shape delta| after PriceShapeModel.from_dict of a persisted shape whose max sits exactly at the guard's bound, and its warnings",
  exp=["at_edge max_abs_shape_delta=2.53448 warnings baseline=0 mutant=1 tail_price_17h baseline=0.5 mutant=0.827586", "cases_moved=1 count (of 8)"],
  direction="up (a profile exactly at the bound is clipped, renormalised and warned about)", null="nextafter below the bound, flat ones, the learner cone max: identical"),
"28de20de50a9540b": dict(sym="price_model:_profile_index (via PriceShapeLearner.fold, PriceShapeModel.predict)", line=155, pert="`weekday() >= 5` -> `weekday() > 5`",
  metric="weekend days learned from one folded Mon..Sun week, and the guessed Saturday 03:00 price at level 1.0",
  exp=["weekend_days baseline=2 mutant=1", "weekday_days baseline=5 mutant=6", "saturday_0300_predict_level1 baseline=0.737143 mutant=0.564779", "null_days_differ=0 count"],
  direction="down (Saturday folds into and is predicted from the weekday profile)", null="Mon-Fri and Sunday index identically"),
"e5eea05f4463602e": dict(sym="price_model:_tibber_post (via pull_prices)", line=844, pert="`if resp.status != 200:` -> `if False:`",
  metric="pull_prices' verdict for a Tibber reply with a given status and body (aiohttp-shaped fake session)",
  exp=["pull_prices_401_html_body verdict baseline=reauth mutant=raised:ContentTypeError", "pull_prices_502_html_body verdict baseline=fail mutant=raised:ContentTypeError", "cases_moved=3 count (of 6)"],
  direction="sign_flip (reauth -> an exception the coordinator catches as an ordinary ClientError fetch failure)", null="JSON error bodies (401, 500) and a 200 with no homes: identical"),
}
EPS = dict(metric="calls of extend_price_series whose (prices, mask, sigma) differ baseline vs mutant, over the coordinator's call shape (step_starts = utc_step_starts(midnight, n_steps, ...))",
           sym="price_model:extend_price_series")
H["3ceb6a076659004f"] = dict(EPS, line=510, pert="`if known_count >= n_steps:` -> `if False:`", exp=["prod_differ=0 count (of 192)", "direct_differ=0 count (of 6)"], direction="none found", null="every production case is its own null (0 differ)")
H["b434193b049a41c3"] = dict(EPS, line=510, pert="`known_count >= n_steps` -> `known_count > n_steps`", exp=["prod_differ=0 count (of 192)", "direct_differ=0 count (of 6)"], direction="none found", null="n_steps 0 and known_count < n_steps cases")
H["29db99dee6a5debd"] = dict(EPS, line=532, pert="`range(min(known_count, len(step_start_times)))` -> `range((known_count))`", exp=["prod_differ=0 count (of 192)", "direct_short_starts_known3_n5_len1 baseline=[0.4, 0.5, 0.6, 0.5, 0.5] mutant=IndexError", "direct_differ=1 count (of 6)"], direction="none in production (len(step_starts) == n_steps > known_count); IndexError off-contract", null="production cases")
H["c1e06ebefdc5abad"] = dict(EPS, line=541, pert="`if i < len(step_start_times)` -> `if i <= len(step_start_times)`", exp=["prod_differ=0 count (of 192)", "direct_short_starts_known1_n4_len2 baseline=[0.4]*4 mutant=IndexError", "direct_differ=2 count (of 6)"], direction="none in production (i < n_steps == len(step_starts)); IndexError off-contract", null="production cases")
H["886591ca08e1d27e"] = dict(EPS, line=535, pert="`if shape_mean > 1e-6:` -> `if shape_mean >= 1e-6:`", exp=["prod_differ=0 count (of 192)", "direct_shape_mean_exactly_1e-6 tail_price baseline=0.0 mutant=0.45", "production_min_shape_for=0.2"], direction="none in production (shape_for >= SHAPE_MIN 0.2 > 1e-6); up only for a model reading exactly 1e-6", null="production cases")
TRAILER = '''

_cpu, _thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
print(f"RESULT thread_factor={_cpu / _thr if _thr > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = next(int(x.split()[1]) for x in open("/proc/vmstat") if x.startswith("pswpin "))
except (OSError, StopIteration):
    _sw = 0
print(f"RESULT swapins={_sw}")
'''
for k, h in H.items():
    p = W / f"probe_{k}.py"
    t = p.read_text()
    cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {REL}/probe_{k}.py"
    head = [f"# Metric: {h['metric']}", f"# Command: {cmd}"]
    head += [f"# EXPECTED RESULT {e}  (exact: counts; tolerance 0)" for e in h["exp"]]
    head += [f"# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: {MACH}.",
             f"# Instrumented symbol: custom_components.heatpump_optimizer.{h['sym']} (price_model.py line {h['line']}).",
             f"# Perturbation: {h['pert']} applied in memory (the function recompiled from its own source, attached",
             f"#   with mock.patch.object for the mutant arm); the gate's tree is never edited. Direction: {h['direction']}.",
             f"# Null control: {h['null']}.",
             "# Count key: the value the production symbol returns (or the learner state it writes), never an input attribute."]
    t = t.replace(f"# HEADER-PENDING {k}", "\n".join(head))
    t = t.replace("import inspect, sys, textwrap, warnings", "import inspect, sys, textwrap, time, warnings\n_T0 = (time.process_time(), time.thread_time())", 1)
    if "RESULT thread_factor" not in t:
        t = t.rstrip("\n") + "\n" + TRAILER
    p.write_text(t)
    print("ok", k)
