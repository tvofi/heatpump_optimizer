"""Reviewer's probe (builder: the reviewer, not the finder): store load/refuse of DutySwitchLearner."""
import sys, copy, json, datetime as dt
sys.path[:0] = ["tests", "custom_components"]
from heatpump_optimizer import duty_switch as ds
t0 = dt.datetime(2026, 1, 1, 12, tzinfo=dt.timezone.utc)
L = ds.DutySwitchLearner()
for i in range(6):
    L.directions["dhw_space"].book(t0 + dt.timedelta(days=i), True, 480.0 + i)
L.directions["space_dhw"].book(t0, False, None)
good = json.loads(json.dumps(L.stored_record()))
back = ds.DutySwitchLearner.from_record(good)
print("RESULT round_trip_equal", back.stored_record() == good, "usable", back.directions["dhw_space"].usable, "n", round(back.directions["dhw_space"].n, 3))
empty = ds.DutySwitchLearner().stored_record()
def is_empty(rec): return ds.DutySwitchLearner.from_record(rec).stored_record() == empty
def mut(path, value, delete=False):
    r = copy.deepcopy(good); node = r
    for p in path[:-1]: node = node[p]
    if delete: del node[path[-1]]
    else: node[path[-1]] = value
    return r
R = ["directions", "dhw_space"]
cases = {
 "none": None, "list": [], "str": "x", "no_directions": {}, "directions_list": {"directions": []},
 "extra_top_key_kept?": {**good, "x": 1},
 "missing_direction": mut(["directions", "space_dhw"], None, True), "extra_direction": mut(["directions", "both"], good["directions"]["dhw_space"]),
 "row_none": mut(R, None), "row_missing_key": mut(R + ["void"], None, True), "row_extra_key": mut(R + ["zz"], 1),
 "k_nan": mut(R + ["k"], float("nan")), "k_inf": mut(R + ["k"], float("inf")), "k_neg": mut(R + ["k"], -0.1), "k_big": mut(R + ["k"], 1e6 + 1), "k_str": mut(R + ["k"], "3"), "k_bool": mut(R + ["k"], True),
 "kept_w_neg": mut(R + ["kept_w"], -1), "usable_int": mut(R + ["usable"], 1), "usable_none": mut(R + ["usable"], None),
 "off_33": mut(R + ["off_s"], [1.0] * 33), "off_neg": mut(R + ["off_s"], [-1.0]), "off_big": mut(R + ["off_s"], [86401.0]), "off_str": mut(R + ["off_s"], ["1"]), "off_dict": mut(R + ["off_s"], {}), "off_bool": mut(R + ["off_s"], [True]),
 "tally_float": mut(R + ["stopped"], 1.0), "tally_neg": mut(R + ["void"], -1), "tally_bool": mut(R + ["kept"], True), "tally_big": mut(R + ["censored"], 10**9 + 1),
 "stamp_garbage": mut(R + ["decayed_at"], "yesterday"), "stamp_int": mut(R + ["decayed_at"], 5), "stamp_empty": mut(R + ["decayed_at"], ""),
 "day_garbage": mut(R + ["first_day"], "2026-13-01"), "day_int": mut(R + ["first_day"], 20260101), "day_one_null": mut(R + ["first_day"], None), "day_order": mut(R + ["first_day"], "2027-01-01"),
}
bad = [n for n, c in cases.items() if not n.endswith("?") and not is_empty(c)]
print("RESULT malformed_cases", len(cases) - 1, "not_emptied", bad)
print("RESULT extra_top_key_loads_whole", not is_empty(cases["extra_top_key_kept?"]))
# shapes that are valid but inconsistent: accepted?
for name, rec in {"usable_true_n0": mut(R + ["k"], 0.0), "future_stamp": mut(R + ["decayed_at"], "2099-01-01T00:00:00+00:00"), "naive_stamp": mut(R + ["decayed_at"], "2026-01-01T00:00:00")}.items():
    lr = ds.DutySwitchLearner.from_record(rec); d = lr.directions["dhw_space"]
    before = (d.usable, round(d.n, 3)); lr.note_pass(t0 + dt.timedelta(days=30), ds.SwitchContext(), True, False)
    print("RESULT accepted_inconsistent", name, "loaded_empty", lr.stored_record() == empty, "before", before, "after_pass", (d.usable, round(d.n, 3)))
# relearn invariant: p unchanged by decay; latch off after avoidance; one episode cannot re-latch
d = ds.DutySwitchLearner.from_record(good).directions["dhw_space"]; p0 = d.p
d.decay(t0 + dt.timedelta(days=60)); print("RESULT decay_p_constant", abs(d.p - p0) < 1e-12, "n", round(d.n, 3), "usable", d.usable)
d.book(t0 + dt.timedelta(days=60), True, None); print("RESULT one_episode_after_off", "n", round(d.n, 3), "usable", d.usable)
# clock stepping backwards never grows a count
d2 = ds.DutySwitchLearner.from_record(good).directions["dhw_space"]; n0 = d2.n; d2.decay(t0 - dt.timedelta(days=400)); print("RESULT backward_clock_n_unchanged", d2.n == n0)
