P = "custom_components.heatpump_optimizer.price_model"
K = {}

K["b10967dd4ea185fd"] = dict(line=72, sym=f"{P}:SHAPE_MIN (read by PriceShapeModel.observe_day's np.clip and RESIDUAL_VAR_MAX)",
 metric="smallest learned hourly shape factor (shapes[weekday] min) after one day folded through PriceShapeLearner.fold",
 body='''
def shape_min(mod, day):
    return round(min(fold(mod, [(WEEKDAYS[0], day)]).model.shapes[0]), 6)
low = list(DAY); low[3] = 0.01
neg = list(DAY); neg[3] = -0.05
compare("shape_min", shape_min, {"winter_day": DAY, "one_hour_0p01": low, "one_hour_negative": neg},
        nulls={"mild_day_ratios_0p8_1p2": [1.0] * 12 + [1.5] * 12, "flat": FLAT})
print(f"RESULT residual_var_max_baseline={B.RESIDUAL_VAR_MAX}")
print(f"RESULT residual_var_max_mutant={M.RESIDUAL_VAR_MAX}")
''')

K["7e5493bcbddd6c18"] = dict(line=80, sym=f"{P}:QUARTER_ALPHA (read by PriceShapeModel.observe_day_quarters' EWMA)",
 metric="learned quarter factor of hour 7 quarter 0 (quarter_factors[weekday][28]) after quarter days folded through PriceShapeLearner.fold",
 body='''
up, down = quarters(DAY), quarters(DAY, ramp=(1.1, 1.03, 0.97, 0.9))
def qf(mod, days):
    return round(fold(mod, list(zip(WEEKDAYS, days))).model.quarter_factors[0][28], 6)
compare("qf_h7q0", qf, {"two_days_up_down": [up, down], "three_days_up_down_up": [up, down, up]},
        nulls={"one_day_seed_only": [up], "two_identical_days": [up, up]})
''')

K["66686e3bc3bac9b9"] = dict(line=81, sym=f"{P}:QUARTER_CONFIDENCE_DAYS (read by PriceShapeModel.quarter_confidence -> quarter_factor -> predict)",
 metric="PriceShapeModel.predict(weekday 07:00, level 1.0) after n quarter days folded through PriceShapeLearner.fold",
 body='''
def pred(mod, n):
    m = fold(mod, [(d, quarters(DAY)) for d in WEEKDAYS[:n]]).model
    return round(m.predict(datetime(2026, 12, 2, 7, 0), 1.0), 6)
compare("predict_0700", pred, {"5_days": 5, "7_days": 7, "1_day": 1}, nulls={"0_days": 0, "10_days": 10})
''')

K["5bf50f5d986f927d"] = dict(line=84, sym=f"{P}:QUARTER_FACTOR_MIN (read by PriceShapeModel.observe_day_quarters' np.clip and _in_domain in from_dict)",
 metric="learned quarter factor of hour 6 quarter 0 after one quarter day folded; and the stored factor after PriceShapeModel.from_dict",
 body='''
def qf(mod, q):
    return round(fold(mod, [(WEEKDAYS[0], q)]).model.quarter_factors[0][24], 6)
steep = quarters(DAY); steep[24:28] = [0.1, 0.5, 0.6, 0.8]
negq = quarters(DAY); negq[24:28] = [-0.2, 0.5, 0.6, 0.8]
compare("qf_h6q0", qf, {"quarter_at_0p2_of_hour": steep, "negative_quarter": negq}, nulls={"ramp_0p9_1p1": quarters(DAY)})
def stored(mod, row):
    data = {"quarter_factors": [row + [1.0] * 92, [1.0] * 96]}
    return round(mod.PriceShapeModel.from_dict(data).quarter_factors[0][0], 6)
compare("stored_q0", stored, {"stored_ratio_9": [0.2, 0.9, 1.1, 1.8]}, nulls={"stored_ratio_2": [0.7, 0.9, 1.0, 1.4]})
''')

K["cc96ce9e391ca6f2"] = dict(line=85, sym=f"{P}:QUARTER_FACTOR_MAX (read by PriceShapeModel.observe_day_quarters' np.clip and _in_domain in from_dict)",
 metric="learned quarter factor of hour 3 quarter 0 after one quarter day folded; and the stored factor after PriceShapeModel.from_dict",
 body='''
def qf(mod, q):
    return round(fold(mod, [(WEEKDAYS[0], q)]).model.quarter_factors[0][12], 6)
spike = quarters(DAY); spike[12:16] = [3.0, -1.0, -1.0, -0.6]     # negative spot quarters: hour mean 0.1, q0 at 30x
mild = quarters(DAY); mild[12:16] = [1.2, -0.2, 0.1, 0.1]          # hour mean 0.3, q0 at 4x..8x (=4.0x)
mild2 = quarters(DAY); mild2[12:16] = [1.5, -0.3, 0.0, 0.0]        # hour mean 0.3, q0 at 5x
compare("qf_h3q0", qf, {"negative_quarters_q0_30x": spike, "negative_quarters_q0_5x": mild2, "q0_exactly_4x": mild},
        nulls={"nonnegative_max_possible_4x": quarters(DAY)[:12] + [0.0, 0.0, 0.0, 4.0][::-1] + quarters(DAY)[16:], "ramp": quarters(DAY)})
def stored(mod, row):
    data = {"quarter_factors": [row + [1.0] * 92, [1.0] * 96]}
    return round(mod.PriceShapeModel.from_dict(data).quarter_factors[0][0], 6)
compare("stored_q0", stored, {"stored_ratio_20": [3.2, 0.16, 0.32, 0.32]}, nulls={"stored_ratio_2": [0.7, 0.9, 1.0, 1.4]})
''')

K["b5aef00760fd5ea8"] = dict(line=90, sym=f"{P}:VAR_ALPHA (read by PriceShapeModel.observe_day's residual-variance EWMA; published via summary() weekday_sigma)",
 metric="published price_prior weekday_sigma[17] (PriceShapeModel.summary) after days folded through PriceShapeLearner.fold",
 body='''
def sig(mod, days):
    return fold(mod, list(zip(WEEKDAYS, days))).model.summary()["weekday_sigma"][17]
compare("weekday_sigma_17", sig, {"two_days_day_reversed": [DAY, DAY2], "three_days": [DAY, DAY2, DAY]},
        nulls={"one_day_seed_only": [DAY]})
''')

K["b9b6cf1d15a84248"] = dict(line=337, sym=f"{P}:PriceShapeModel.expected_daily_min (caller coordinator.py:4373, the #47 legionella price ceiling)",
 metric="PriceShapeModel.expected_daily_min(day_types, level) on a model with 5 folded weekday and weekend days: value, None, or the exception raised",
 body='''
def edm(mod, args):
    days = [(d, DAY) for d in WEEKDAYS[:5]] + [(d, DAY2) for d in ("2026-11-21", "2026-11-22", "2026-11-28", "2026-11-29", "2026-12-05")]
    m = fold(mod, days).model
    out = m.expected_daily_min(*args)
    return None if out is None else round(out, 6)
compare("edm", edm, {"empty_day_types_level_0p8": ([], 0.8), "level_nan": ([0], float("nan")),
                     "level_zero": ([0], 0.0), "level_negative": ([0, 1], -0.4), "level_inf": ([0], float("inf"))},
        nulls={"normal_level_0p8": ([0, 1], 0.8)})
# Production reach of the empty list: coordinator.py builds day_types from the days strictly after today up to the
# legionella deadline's date; an overdue or due-today cycle leaves it empty, and level > 1e-6 is the only guard there.
src = (ROOT / "custom_components/heatpump_optimizer/coordinator.py").read_text()
i = src.index("self._price_model.expected_daily_min(")
blk = src[max(0, i - 1500):i]
print(f"RESULT reach_caller_guards_empty_day_types={int('if day_types' in blk or 'and day_types' in blk)} count")
''')

K["a5c9796d35117839"] = dict(line=342, sym=f"{P}:PriceShapeModel.expected_daily_min (caller coordinator.py:4373, the #47 legionella price ceiling)",
 metric="PriceShapeModel.expected_daily_min([weekday], 0.8) after n weekdays folded through PriceShapeLearner.fold",
 body='''
def edm(mod, n):
    out = fold(mod, [(d, DAY) for d in WEEKDAYS[:n]]).model.expected_daily_min([0], 0.8)
    return None if out is None else round(out, 6)
compare("edm", edm, {"5_days_exactly_confident": 5}, nulls={"4_days": 4, "6_days": 6})
''')

K["13cadf1ab9a2de61"] = dict(line=400, sym=f"{P}:PriceShapeModel.from_dict (residual_var load gate; caller PriceShapeLearner.restore / adopt_model)",
 metric="residual_var[weekday][0] after PriceShapeModel.from_dict of a stored variance row",
 body='''
def load(mod, v):
    data = {"residual_var": [[v] + [0.5] * 23, [0.5] * 24]}
    return mod.PriceShapeModel.from_dict(data).residual_var[0][0]
cap = B.RESIDUAL_VAR_MAX
compare("var_loaded", load, {"exactly_cap_225": cap}, nulls={"below_cap_224p9": cap - 0.1, "above_cap_225p1": cap + 0.1, "typical_0p3": 0.3})
# Reach: the largest variance the learner itself writes over an adversarial sequence (5 days spiking at 00:00,
# then a day spiking at 12:00, all clipped to the shape cone), versus the cap.
spk = [0.01] * 24; spk[0] = 30.0
spk2 = [0.01] * 24; spk2[12] = 30.0
m = fold(B, [(d, spk) for d in WEEKDAYS[:5]] + [(WEEKDAYS[5], spk2)]).model
print(f"RESULT reach_max_var_written_adversarial={max(max(r) for r in m.residual_var):.4f} (cap {cap})")
''')

K["b5a482468c783209"] = dict(line=207, sym=f"{P}:PriceShapeModel.observe_day (mean guard; caller PriceShapeLearner.fold)",
 metric="days[weekday] after one hourly day folded through PriceShapeLearner.fold (1 = the day was learned)",
 body='''
edge = [0.0] * 12 + [2e-6] * 12
print(f"RESULT mean_is_exact={int(float(np.mean(np.asarray(edge))) == 1e-6)} count")
def days(mod, day):
    return fold(mod, [(WEEKDAYS[0], day)]).model.days[0]
compare("days_learned", days, {"mean_exactly_1e-6": edge}, nulls={"mean_zero": [0.0] * 24, "winter_day": DAY, "mean_2e-6": [2e-6] * 24})
''')

K["0b10a7c76e2514d2"] = dict(line=219, sym=f"{P}:PriceShapeModel.observe_day (first-day residual-variance seed; caller PriceShapeLearner.fold)",
 metric="published price_prior weekday_sigma[17] (PriceShapeModel.summary) after one hourly day folded through PriceShapeLearner.fold",
 body='''
def sig(mod, days):
    return fold(mod, list(zip(WEEKDAYS, days))).model.summary()["weekday_sigma"][17]
compare("weekday_sigma_17", sig, {"one_winter_day": [DAY], "one_reversed_day": [DAY2]}, nulls={"one_flat_day": [FLAT]})
''')

K["c4697335da324182"] = dict(line=226, sym=f"{P}:PriceShapeModel.observe_day (first-day shape seed; caller PriceShapeLearner.fold)",
 metric="published price_prior weekday_shape[17] (PriceShapeModel.summary) after one hourly day folded through PriceShapeLearner.fold",
 body='''
def shp(mod, days):
    return fold(mod, list(zip(WEEKDAYS, days))).model.summary()["weekday_shape"][17]
compare("weekday_shape_17", shp, {"one_winter_day": [DAY], "five_winter_days": [DAY] * 5}, nulls={"one_flat_day": [FLAT]})
''')

K["79c65c4903e72ee2"] = dict(line=232, sym=f"{P}:PriceShapeModel.observe_day (renormalisation floor; caller PriceShapeLearner.fold)",
 metric="shapes[weekday][17] after observe_day: through production (fold, from_dict-restored models) and on a hand-built model whose stored shape is negative",
 body='''
def prod(mod, days):
    return fold(mod, list(zip(WEEKDAYS, days))).model.shapes[0][17]
compare("shape17_production", prod, {"one_day": [DAY], "two_days": [DAY, DAY2], "spiky_days": [[0.01] * 23 + [30.0], [30.0] + [0.01] * 23]},
        nulls={})
def restored(mod, row):
    m = mod.PriceShapeModel.from_dict({"shapes": [row, [1.0] * 24], "days": [3, 0]})
    m.observe_day(WED, DAY)
    return m.shapes[0][17]
compare("shape17_from_dict", restored, {"stored_negative_row": [-1.0] * 24, "stored_zero_row": [0.0] * 24, "stored_tiny_row": [1e-9] * 24})
def handbuilt(mod, row):
    m = mod.PriceShapeModel(shapes=[list(row), [1.0] * 24], days=[3, 0])
    m.observe_day(WED, DAY)
    return m.shapes[0][17]
compare("shape17_handbuilt", handbuilt, {"negative_row_bypassing_from_dict": [-1.0] * 24})
''')

K["4e79ba6ea642d086"] = dict(line=258, sym=f"{P}:PriceShapeModel.observe_day_quarters (usable-hour guard; caller PriceShapeLearner.fold)",
 metric="learned quarter factor of hour 3 quarter 3 (quarter_factors[weekday][15]) after one quarter day folded through PriceShapeLearner.fold",
 body='''
def qf(mod, q):
    return round(fold(mod, [(WEEKDAYS[0], q)]).model.quarter_factors[0][15], 6)
edge = quarters(DAY); edge[12:16] = [0.0, 0.0, 0.0, 4e-6]
print(f"RESULT hour_mean_is_exact={int(float(np.mean(np.asarray(edge[12:16]))) == 1e-6)} count")
compare("qf_h3q3", qf, {"hour_mean_exactly_1e-6": edge},
        nulls={"hour_all_zero": quarters(DAY)[:12] + [0.0] * 4 + quarters(DAY)[16:], "ramp": quarters(DAY)})
''')

K["12cd6ddd79fb36fc"] = dict(line=269, sym=f"{P}:PriceShapeModel.observe_day_quarters (first-day quarter seed; caller PriceShapeLearner.fold)",
 metric="PriceShapeModel.predict(weekday 07:00, level 1.0) after five quarter days folded through PriceShapeLearner.fold, and the learned factor quarter_factors[weekday][28] after one",
 body='''
def qf(mod, n):
    return round(fold(mod, [(d, quarters(DAY)) for d in WEEKDAYS[:n]]).model.quarter_factors[0][28], 6)
def pred(mod, n):
    return round(fold(mod, [(d, quarters(DAY)) for d in WEEKDAYS[:n]]).model.predict(datetime(2026, 12, 2, 7, 0), 1.0), 6)
compare("qf_h7q0", qf, {"1_day": 1, "5_days": 5})
compare("predict_0700", pred, {"5_days": 5}, nulls={"0_days": 0})
def flat(mod, n):
    return round(fold(mod, [(d, [1.0] * 96) for d in WEEKDAYS[:n]]).model.quarter_factors[0][28], 6)
compare("qf_flat_quarters", flat, {}, nulls={"1_flat_day": 1})
''')

K["cee6857510fbe69e"] = dict(line=275, sym=f"{P}:PriceShapeModel.observe_day_quarters (per-hour renormalisation floor; caller PriceShapeLearner.fold)",
 metric="quarter_factors[weekday][12] after observe_day_quarters: through production (fold, from_dict-restored) and on a hand-built model whose stored factors are negative",
 body='''
zero_hour = quarters(DAY); zero_hour[12:16] = [0.0, 0.0, 0.0, 0.0]
negh = quarters(DAY); negh[12:16] = [-0.5, -0.5, -0.5, -0.5]
spike = quarters(DAY); spike[12:16] = [3.0, -1.0, -1.0, -0.6]
def prod(mod, days):
    return fold(mod, list(zip(WEEKDAYS, days))).model.quarter_factors[0][12]
compare("qf12_production", prod, {"zero_price_hour": [zero_hour], "negative_hour_two_days": [quarters(DAY), negh],
                                  "spike_then_zero": [spike, zero_hour, spike]})
def restored(mod, row):
    m = mod.PriceShapeModel.from_dict({"quarter_factors": [[1.0] * 12 + row + [1.0] * 80, [1.0] * 96], "quarter_days": [2, 0]})
    m.observe_day_quarters(WED, zero_hour)
    return m.quarter_factors[0][12]
compare("qf12_from_dict", restored, {"stored_negative": [-1.0] * 4, "stored_zero": [0.0] * 4})
def handbuilt(mod, row):
    m = mod.PriceShapeModel(quarter_factors=[[1.0] * 12 + row + [1.0] * 80, [1.0] * 96], quarter_days=[2, 0])
    m.observe_day_quarters(WED, zero_hour)
    return m.quarter_factors[0][12]
compare("qf12_handbuilt", handbuilt, {"negative_bypassing_from_dict": [-1.0] * 4})
''')
