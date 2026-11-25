B = {}
B["3e3fbb5fcbbe9bcc"] = dict(
metric="INFO records 'a pre-v5.3.0 store was upgraded' DefrostDerate.from_dict logs for a v1 store (factors/counts only), plus the restored `migrated` flag and factor grid (state the diagnostics publish).",
expected="upgrade_log_records_baseline=1, upgrade_log_records_mutant=0; migrated True and factors identical in both arms",
symbol="custom_components.heatpump_optimizer.defrost:DefrostDerate.from_dict, line 566",
pert="key 3e3fbb5fcbbe9bcc GUARD_OFF, `if instance.migrated:` -> `if False:`, in memory (the classmethod re-compiled and patched onto the class). Direction: 1 -> 0 log records; state unchanged.",
null="a v2 store (duty grids present), where `migrated` is False and the guard is false either way.",
body='''
from custom_components.heatpump_optimizer import defrost as d
OLD = "            if instance.migrated:"
mut = mutated(d.DefrostDerate.from_dict, d, OLD, "            if False:")  # a classmethod object (the decorator is in the source)
src = d.DefrostDerate()
src.observe(0.0, 90.0, 0.8)
v2 = src.as_dict()
v1 = {"factors": v2["factors"], "counts": v2["counts"]}
for label, store in (("v1_store", v1), ("v2_store", v2)):
    for arm in ("baseline", "mutant"):
        out = {}
        def go():
            if arm == "mutant":
                with mock.patch.object(d.DefrostDerate, "from_dict", mut):
                    out["i"] = d.DefrostDerate.from_dict(dict(store))
            else:
                out["i"] = d.DefrostDerate.from_dict(dict(store))
        n = logged(d.__name__, "store was upgraded", go)
        inst = out["i"]
        print(f"RESULT {label}_upgrade_log_records_{arm}={n} count")
        print(f"RESULT {label}_migrated_{arm}={inst.migrated!r}")
        print(f"RESULT {label}_factors_equal_source_{arm}={int(inst.factors == src.factors)}")
''')
_unit = '''
from custom_components.heatpump_optimizer import defrost as d
OLD = "            return 0.0 <= v <= 1.0  # observe_duty's gate; NaN fails it"
NEW = OLD.replace(%r, %r)
mut = mutated(d.DefrostDerate.from_dict, d, OLD, NEW)  # a classmethod object (the decorator is in the source)
moved = 0
for duty in (0.0, 0.5, 1.0, 0.25):
    src = d.DefrostDerate()
    for _ in range(12):
        src.observe_duty(0.0, 90.0, duty)
    t, h = src._bucket(0.0, 90.0)
    store = src.as_dict()
    store["duty"][t][h] = duty  # the cell holds exactly the edge value
    b = d.DefrostDerate.from_dict(store)
    with mock.patch.object(d.DefrostDerate, "from_dict", mut):
        m = d.DefrostDerate.from_dict(store)
    for arm, inst in (("baseline", b), ("mutant", m)):
        print(f"RESULT duty{duty}_restored_duty_count_{arm}={inst.duty_counts[t][h]} count")
        print(f"RESULT duty{duty}_published_factor_{arm}={inst.factor(0.0, 90.0)!r}")
    moved += b.duty_counts[t][h] != m.duty_counts[t][h]
    if duty == 0.0:
        cells_b = sum(n > 0 for row in b.duty_counts for n in row)
        cells_m = sum(n > 0 for row in m.duty_counts for n in row)
        print(f"RESULT duty0.0_measured_cells_kept_baseline={cells_b} count")
        print(f"RESULT duty0.0_measured_cells_kept_mutant={cells_m} count")
print(f"RESULT duties_moved={moved} count")
# The consequence on a bucket that also carries a learned inferred derate (0.8 over 12 samples):
# a reset measured half hands the bucket back to the inferred estimator.
for duty in (0.0, 1.0):
    src = d.DefrostDerate()
    t, h = src._bucket(0.0, 90.0)
    src.factors[t][h], src.counts[t][h] = 0.8, 12
    src.duty[t][h], src.duty_counts[t][h] = duty, 12
    store = src.as_dict()
    b = d.DefrostDerate.from_dict(store)
    with mock.patch.object(d.DefrostDerate, "from_dict", mut):
        m = d.DefrostDerate.from_dict(store)
    print(f"RESULT with_inferred_duty{duty}_factor_before_restore={src.factor(0.0, 90.0)!r}")
    print(f"RESULT with_inferred_duty{duty}_factor_after_restore_baseline={b.factor(0.0, 90.0)!r}")
    print(f"RESULT with_inferred_duty{duty}_factor_after_restore_mutant={m.factor(0.0, 90.0)!r}")
'''
B["1ba9abbe8e702464"] = dict(
metric="the duty count a DefrostDerate bucket keeps across as_dict -> from_dict when its stored duty is exactly 1.0 (12 = kept, 0 = the bucket restarts unmeasured), and the factor published after the restore.",
expected="duty1.0_restored_duty_count_baseline=12, mutant=0; duties 0.0, 0.25, 0.5 identical",
symbol="custom_components.heatpump_optimizer.defrost:DefrostDerate.from_dict._unit, line 537",
pert="key 1ba9abbe8e702464 CMP_BOUND, `0.0 <= v <= 1.0` -> `0.0 <= v < 1.0`, in memory (from_dict re-compiled, its nested _unit with it). Direction: a duty-1.0 cell kept -> reset.",
null="stored duties 0.25 and 0.5, where neither bound is tied.",
body=_unit % ("v <= 1.0", "v < 1.0"))
B["4aac8e694ddc5dfe"] = dict(
metric="the duty count a DefrostDerate bucket keeps across as_dict -> from_dict when its stored duty is exactly 0.0 (12 = kept, 0 = the bucket restarts unmeasured), the factor published after the restore, and how many measured cells a store of zero-duty buckets keeps.",
expected="duty0.0_restored_duty_count_baseline=12, mutant=0; duties 0.25, 0.5, 1.0 identical",
symbol="custom_components.heatpump_optimizer.defrost:DefrostDerate.from_dict._unit, line 537",
pert="key 4aac8e694ddc5dfe CMP_BOUND, `0.0 <= v <= 1.0` -> `0.0 < v <= 1.0`, in memory. Direction: a zero-duty cell (the commonest measured observation: 'no defrost happened') kept -> reset at every restart.",
null="stored duties 0.25, 0.5 and 1.0, where the lower bound is not tied.",
body=_unit % ("0.0 <= v", "0.0 < v"))
_obs = '''
from custom_components.heatpump_optimizer import defrost as d
OLD = "        if delivered_ratio <= 0 or delivered_ratio > 3.0:"
mut = mutated(d.DefrostDerate.observe, d, OLD, OLD.replace(%r, %r))
moved = 0
for ratio in (0.0, 3.0, 1e-9, 2.999999, 3.000001, 1.0):
    out = {}
    for arm, fn in (("baseline", d.DefrostDerate.observe), ("mutant", mut)):
        dd = d.DefrostDerate()
        t, h = dd._bucket(0.0, 90.0)
        fn(dd, 0.0, 90.0, ratio)
        out[arm] = (dd.counts[t][h], dd.factors[t][h])
        print(f"RESULT ratio{ratio}_count_{arm}={dd.counts[t][h]} count")
        print(f"RESULT ratio{ratio}_factor_{arm}={dd.factors[t][h]!r}")
    moved += out["baseline"] != out["mutant"]
print(f"RESULT ratios_moved={moved} count")
# On a bucket already learned to 0.8 over 6 samples (half trust), the edge ratio's fold moves the factor.
for ratio in (0.0, 3.0):
    for arm, fn in (("baseline", d.DefrostDerate.observe), ("mutant", mut)):
        dd = d.DefrostDerate()
        t, h = dd._bucket(0.0, 90.0)
        dd.factors[t][h], dd.counts[t][h] = 0.8, 6
        fn(dd, 0.0, 90.0, ratio)
        print(f"RESULT learned_ratio{ratio}_published_factor_{arm}={dd.factor(0.0, 90.0)!r}")
'''
B["5366f1e6254f603c"] = dict(
metric="samples DefrostDerate.observe folds into a bucket (counts) and the resulting factor for delivered_ratio exactly 0.0 (1 = folded, 0 = dropped).",
expected="ratio0.0_count_baseline=0, mutant=1 (factor 1.0 -> 0.9775, the target clamped to DERATE_MIN); other ratios identical",
symbol="custom_components.heatpump_optimizer.defrost:DefrostDerate.observe, line 392",
pert="key 5366f1e6254f603c CMP_BOUND, `delivered_ratio <= 0` -> `delivered_ratio < 0`, in memory. Direction: a zero ratio dropped -> folded as the deepest derate.",
null="ratios 1e-9, 1.0, 2.999999, where the lower bound is not tied.",
body=_obs % ("delivered_ratio <= 0 ", "delivered_ratio < 0 "))
B["efb33eb6212be24e"] = dict(
metric="samples DefrostDerate.observe folds into a bucket (counts) and the resulting factor for delivered_ratio exactly 3.0 (1 = folded, 0 = dropped).",
expected="ratio3.0_count_baseline=1, mutant=0; other ratios identical",
symbol="custom_components.heatpump_optimizer.defrost:DefrostDerate.observe, line 392",
pert="key efb33eb6212be24e CMP_BOUND, `delivered_ratio > 3.0` -> `delivered_ratio >= 3.0`, in memory. Direction: a 3.0 ratio folded -> dropped.",
null="ratios 2.999999, 3.000001, 1.0, where the upper bound is not tied.",
body=_obs % ("delivered_ratio > 3.0", "delivered_ratio >= 3.0"))
B["0e3569fef6b39497"] = dict(
metric="INFO 'takes over from the inferred estimate' records DefrostDerate.observe_duty logs when a bucket's duty count reaches DERATE_CONFIDENCE_SAMPLES, for a bucket with NO inferred samples (counts 0) and one with some; plus the bucket's grids after the 12 folds.",
expected="no_inferred_handover_logs_baseline=0, mutant=1; with_inferred 1 in both arms; grids identical",
symbol="custom_components.heatpump_optimizer.defrost:DefrostDerate.observe_duty, line 434",
pert="key 0e3569fef6b39497 CMP_BOUND, `self.counts[t][h] > 0` -> `self.counts[t][h] >= 0`, in memory. Direction: 0 -> 1 handover log on a bucket that had nothing to hand over from (it reports 'inferred estimate 1.000 -> x').",
null="a bucket with inferred samples (counts 3), where the comparison is true either way.",
body='''
from custom_components.heatpump_optimizer import defrost as d
OLD = "            and self.counts[t][h] > 0"
mut = mutated(d.DefrostDerate.observe_duty, d, OLD, OLD.replace("> 0", ">= 0"))
for label, n_inf in (("no_inferred", 0), ("with_inferred", 3)):
    grids = {}
    for arm, fn in (("baseline", d.DefrostDerate.observe_duty), ("mutant", mut)):
        dd = d.DefrostDerate()
        for _ in range(n_inf):
            dd.observe(0.0, 90.0, 0.8)
        n = logged(d.__name__, "takes over from the inferred", lambda: [fn(dd, 0.0, 90.0, 0.1) for _ in range(12)])
        grids[arm] = (dd.as_dict(), dd.factor(0.0, 90.0))
        print(f"RESULT {label}_handover_logs_{arm}={n} count")
    print(f"RESULT {label}_state_equal={int(grids['baseline'] == grids['mutant'])}")
''')
