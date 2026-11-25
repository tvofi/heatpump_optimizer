B = {}
B["89bec0a0291b4756"] = dict(
metric="whether _storable_sample_count accepts a stored learner sample count of exactly 2**31 (1 accepted with its int, 0 raised ValueError: the learned value is then discarded on load).",
expected="accepted_2^31_baseline=1, accepted_2^31_mutant=0; 2**31-1 and 2**31+1 identical in both arms",
symbol="custom_components.heatpump_optimizer.coordinator:_storable_sample_count, line 467",
pert="key 89bec0a0291b4756 CMP_BOUND, `not 0 <= count <= 2**31` -> `not 0 <= count < 2**31`, in memory. Direction: accepted -> rejected at the tie.",
null="counts 2**31-1 and 2**31+1 and 0, where the upper bound is not tied.",
body='''
from custom_components.heatpump_optimizer import coordinator as c
OLD = "if not np.isfinite(count) or not 0 <= count <= 2**31:"
mut = mutated(c._storable_sample_count, c, OLD, OLD.replace("count <= 2**31", "count < 2**31"))


def acc(fn, raw):
    try:
        return 1, fn(raw)
    except ValueError:
        return 0, None


moved = 0
for name, raw in (("0", 0), ("2^31-1", 2**31 - 1), ("2^31", 2**31), ("2^31+1", 2**31 + 1), ("2^31_float", float(2**31))):
    (ba, bv), (ma, mv) = acc(c._storable_sample_count, raw), acc(mut, raw)
    print(f"RESULT accepted_{name}_baseline={ba} (value {bv!r})")
    print(f"RESULT accepted_{name}_mutant={ma} (value {mv!r})")
    moved += ba != ma
print(f"RESULT inputs_moved={moved} count")
''')
B["b028ad9d6c702965"] = dict(
metric="length of the warm-start plan _warm_seeded hands the fresh per-solve optimizer (`_prev_shipped_plan`) when the coordinator holds a previous plan (0 = no warm start).",
expected="warm_plan_len_baseline=96, warm_plan_len_mutant=0 (attribute absent); cold start (no previous plan) 0 in both arms",
symbol="custom_components.heatpump_optimizer.coordinator:_warm_seeded, line 2360 (read by optimizer.py HeatPumpOptimizer via getattr(self, '_prev_shipped_plan', None) as one extra multi-start candidate)",
pert="key b028ad9d6c702965 GUARD_OFF, `if result is not None:` -> `if False:`, in memory. Direction: 96 -> 0: the MPC warm start (#1295) is never seeded.",
null="a cold start (`_optimization_result` None), where the guard is false either way.",
body='''
import numpy as np
from custom_components.heatpump_optimizer import coordinator as c
OLD = "    if result is not None:"
mut = mutated(c._warm_seeded, c, OLD, "    if False:")
plan = SimpleNamespace(power_schedule=list(np.linspace(0.5, 2.5, 96)))
for label, prev in (("previous_plan", plan), ("cold_start", None)):
    for arm, fn in (("baseline", c._warm_seeded), ("mutant", mut)):
        coord = SimpleNamespace(_optimization_result=prev)
        opt = fn(coord, SimpleNamespace())
        seeded = getattr(opt, "_prev_shipped_plan", None)
        print(f"RESULT {label}_warm_plan_len_{arm}={0 if seeded is None else len(seeded)} count")
''')
B["3b9eddc7ba9a7488"] = dict(
metric="the inferred derate factor a fresh DefrostDerate bucket holds after one observe(0 C, 90 % RH, delivered_ratio=0.8) and after 12 such observations.",
expected="factor_after_1_baseline=0.99, factor_after_1_mutant=0.98; after_12 0.892 vs 0.814 (approx)",
symbol="custom_components.heatpump_optimizer.defrost:DefrostDerate.observe (reads DERATE_ALPHA at defrost.py:400); constant at defrost.py:124",
pert="key 3b9eddc7ba9a7488 CONST, `DERATE_ALPHA = 0.05` -> `DERATE_ALPHA = 0.1`, in memory (mock.patch.object on the module). Direction: the factor falls twice as fast.",
null="delivered_ratio 1.0 (the target equals the start), where the rate cannot move the factor.",
body='''
from custom_components.heatpump_optimizer import defrost as d
for ratio in (0.8, 1.0):
    for arm, alpha in (("baseline", d.DERATE_ALPHA), ("mutant", 0.1)):
        with mock.patch.object(d, "DERATE_ALPHA", alpha):
            dd = d.DefrostDerate()
            t, h = dd._bucket(0.0, 90.0)
            vals = []
            for i in range(12):
                dd.observe(0.0, 90.0, ratio)
                vals.append(dd.factors[t][h])
        print(f"RESULT ratio{ratio}_factor_after_1_{arm}={vals[0]:.6f}")
        print(f"RESULT ratio{ratio}_factor_after_12_{arm}={vals[-1]:.6f}")
        print(f"RESULT ratio{ratio}_published_factor_after_12_{arm}={dd.factor(0.0, 90.0):.6f}")
''')
B["fc4fe0f49de831a8"] = dict(
metric="the derate derate_from_duty returns over a grid of measured duties 0..1 (step 0.01), and the derate DefrostDerate.factor publishes for a bucket trusted at duty 0.5: count of grid points whose value differs between arms, and the largest difference.",
expected="points_differ: only duties above 0.30, by at most 1 ulp (5.6e-17): DERATE_MIN (0.55) already equals 1 - 1.5 * 0.30, so the duty cap binds nowhere the DERATE_MIN floor does not",
symbol="custom_components.heatpump_optimizer.defrost:derate_from_duty (reads DEFROST_DUTY_MAX at defrost.py:204); constant at defrost.py:142",
pert="key fc4fe0f49de831a8 CONST, `DEFROST_DUTY_MAX = 0.30` -> `DEFROST_DUTY_MAX = 0.6`, in memory (mock.patch.object). Direction searched: any duty whose derate changes.",
null="duties 0..0.30, where neither cap binds: identical.",
body='''
from custom_components.heatpump_optimizer import defrost as d
print(f"RESULT derate_min={d.DERATE_MIN!r}")
print(f"RESULT one_minus_loss_x_cap={1.0 - d.DEFROST_DUTY_MAX * d.DEFROST_LOSS_MULTIPLIER!r}")
grid = [i / 100 for i in range(101)] + [0.299999, 0.300001, 0.3666667, 2.0, -0.1]
diff, maxd, maxd_gt_ulp = 0, 0.0, 0
for x in grid:
    b = d.derate_from_duty(x)
    with mock.patch.object(d, "DEFROST_DUTY_MAX", 0.6):
        m = d.derate_from_duty(x)
    if b != m:
        diff += 1
        maxd = max(maxd, abs(b - m))
        maxd_gt_ulp += abs(b - m) > 1e-12
print(f"RESULT grid_points={len(grid)} count")
print(f"RESULT points_differ={diff} count")
print(f"RESULT points_differ_beyond_1e-12={maxd_gt_ulp} count")
print(f"RESULT max_abs_diff={maxd!r}")
for arm, cap in (("baseline", d.DEFROST_DUTY_MAX), ("mutant", 0.6)):
    with mock.patch.object(d, "DEFROST_DUTY_MAX", cap):
        dd = d.DefrostDerate()
        for _ in range(12):
            dd.observe_duty(0.0, 90.0, 0.5)
        print(f"RESULT published_factor_duty0.5_{arm}={dd.factor(0.0, 90.0)!r}")
        print(f"RESULT summary_derate_duty0.5_{arm}={[r['derate'] for r in dd.summary()]!r}")
''')
B["d1197dfed14a6927"] = dict(
metric="the estimator DefrostDerate._decide names (source, value, samples) for a bucket whose inferred and measured trust-blended derates are exactly equal while the duty count is below DERATE_CONFIDENCE_SAMPLES; source is published per bucket in summary() (the diagnostics attribute).",
expected="tie_source_baseline='measured', tie_source_mutant='inferred'; value identical; a different-count tie also moves `samples`",
symbol="custom_components.heatpump_optimizer.defrost:DefrostDerate._decide, line 313 (read by summary() and factor())",
pert="key d1197dfed14a6927 CMP_BOUND, `if inferred < measured:` -> `if inferred <= measured:`, in memory. Direction: source 'measured' -> 'inferred' at the tie.",
null="inferred strictly above / below measured, where the comparison is not tied.",
body='''
from custom_components.heatpump_optimizer import defrost as d
OLD = "        if inferred < measured:"
mut = mutated(d.DefrostDerate._decide, d, OLD, "        if inferred <= measured:")


def bucket(factor, n_inf, duty, n_duty):
    dd = d.DefrostDerate()
    t, h = dd._bucket(0.0, 90.0)
    dd.factors[t][h], dd.counts[t][h] = factor, n_inf
    dd.duty[t][h], dd.duty_counts[t][h] = duty, n_duty
    return dd, t, h


def _diff_count_tie(duty=0.2, n_duty=3):
    """The first inferred count (!= n_duty) and factor whose trust-blended value equals
    the measured one bit for bit, searched rather than assumed (float ties are exact or absent)."""
    target = d.DefrostDerate._trusted(d.derate_from_duty(duty), n_duty)
    for n in range(1, d.DERATE_CONFIDENCE_SAMPLES):
        if n == n_duty:
            continue
        trust = min(1.0, n / d.DERATE_CONFIDENCE_SAMPLES)
        for f in (1.0 + (target - 1.0) / trust,):
            for g in (f, f + 1e-16, f - 1e-16, f + 2e-16, f - 2e-16):
                if d.DefrostDerate._trusted(g, n) == target:
                    return (g, n, duty, n_duty)
    return (0.8, 6, duty, n_duty)


cases = {
    "tie_same_count": (d.derate_from_duty(0.1), 5, 0.1, 5),
    "tie_diff_count": _diff_count_tie(),
    "inferred_lower": (0.7, 6, 0.1, 5),
    "inferred_higher": (0.99, 6, 0.2, 5),
}
moved = 0
for name, args in cases.items():
    dd, t, h = bucket(*args)
    tie = d.DefrostDerate._trusted(dd.factors[t][h], dd.counts[t][h]) == d.DefrostDerate._trusted(d.derate_from_duty(dd.duty[t][h]), dd.duty_counts[t][h])
    b = dd._decide(t, h)
    m = mut(dd, t, h)
    with mock.patch.object(d.DefrostDerate, "_decide", mut):
        ms = [(r["source"], r["samples"]) for r in dd.summary()]
    bs = [(r["source"], r["samples"]) for r in dd.summary()]
    print(f"RESULT {name}_exact_tie={int(tie)}")
    print(f"RESULT {name}_decide_baseline={b!r}")
    print(f"RESULT {name}_decide_mutant={m!r}")
    print(f"RESULT {name}_summary_baseline={bs!r}")
    print(f"RESULT {name}_summary_mutant={ms!r}")
    moved += b != m
print(f"RESULT cases_moved={moved} count")
''')
