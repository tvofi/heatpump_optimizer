from custom_components.heatpump_optimizer import defrost  # noqa: E402

OLD = "return len(edges) - 2 if value >= edges[-1] else 0"
NEW = "return len(edges) - 2 if value > edges[-1] else 0"
MUT = mutated(defrost, defrost._bucket_index, OLD, NEW)
TE, HE = defrost.TEMP_EDGES, defrost.HUMIDITY_EDGES
inputs = [TE[-1], HE[-1], TE[0], -31.0, 41.0, float("inf"), float("-inf"), float("nan"), 39.999999, 3.0]
moved = []
for v in inputs:
    for nm, edges in (("temp", TE), ("hum", HE)):
        b, m = defrost._bucket_index(v, edges), MUT(v, edges)
        if b != m:
            moved.append(f"{nm}:{v}")
print(f"RESULT bucket_temp_at_top_edge baseline={defrost._bucket_index(TE[-1], TE)} mutant={MUT(TE[-1], TE)}")
print(f"RESULT direct_inputs_moved={len(moved)} of {2 * len(inputs)} ({','.join(moved)})")


def duty_bucket(fn, outdoor, humidity):
    """The (t, h) bucket one measured duty lands in, through DefrostDerate.observe_duty (the production fold)."""
    d = defrost.DefrostDerate()
    with mock.patch.object(defrost, "_bucket_index", fn):
        d.observe_duty(outdoor, humidity, 0.0, events=0)
    return [(t, h) for t in range(len(TE) - 1) for h in range(len(HE) - 1) if d.duty_counts[t][h]][0]


b, m = duty_bucket(defrost._bucket_index, 40.0, 50.0), duty_bucket(MUT, 40.0, 50.0)
print(f"RESULT observe_duty_40C_bucket baseline={b} mutant={m}")
print(f"RESULT observe_duty_40C_moved={int(b != m)} count")
# The consequence on the coldest bucket's learned factor: ten zero-duty 40.0 C settlements on top of a bucket that
# had measured a 0.2 duty at -10 C (twelve samples).
def cold_factor(fn):
    d = defrost.DefrostDerate()
    for _ in range(12):
        d.observe_duty(-10.0, 50.0, 0.2, events=1)
    with mock.patch.object(defrost, "_bucket_index", fn):
        for _ in range(10):
            d.observe_duty(40.0, 50.0, 0.0, events=0)
    return round(d.factor(-17.5, 35.0), 6)


print(f"RESULT cold_bucket_factor baseline={cold_factor(defrost._bucket_index)} mutant={cold_factor(MUT)}")
b, m = duty_bucket(defrost._bucket_index, 20.0, 50.0), duty_bucket(MUT, 20.0, 50.0)
print(f"RESULT null_delta={int(b != m)} count  (20 C: inside the edges, line 169 never runs)")
# Reach: _settle_defrost (coordinator.py:9981) folds observe_duty at ANY outdoor temperature once the flag is legible;
# observe() (inferred) only inside the frost band [FROST_BAND_MIN_C, FROST_BAND_MAX_C), where 40.0 never arrives.
print(f"RESULT frost_band={defrost.FROST_BAND_MIN_C}..{defrost.FROST_BAND_MAX_C} C")
footer()
