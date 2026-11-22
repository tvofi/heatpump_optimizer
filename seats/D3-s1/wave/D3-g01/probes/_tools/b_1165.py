

def drive(electrical_kw, step, commanded=3.0, modelled=3.0):
    """One COP interval: `commanded` kW of heat asked, `electrical_kw` drawn, modelled COP `modelled`, scale 1.0."""
    c = coord()
    c._apply_cop_scale(1.0)
    n0 = c._cop_samples
    with mock.patch.object(co, "COP_LEARNING_MAX_STEP", step), \
         mock.patch.object(co, "probe_install", lambda cfg: SimpleNamespace(cop_sample=lambda h, d: False)):
        refused = c._fold_cop_evidence(commanded, electrical_kw, None, (modelled, False, None))
    return refused, c._cop_samples - n0, round(float(c._cop_scale), 6)


b, m = drive(0.5, 0.05), drive(0.5, 0.1)
print(f"RESULT cop_scale_outlier_baseline={b[2]} (refused={b[0]}, samples={b[1]})")
print(f"RESULT cop_scale_outlier_mutant={m[2]} (refused={m[0]}, samples={m[1]})")
for e in (1.0, 0.3, 0.1, 60.0):
    print(f"RESULT inputs electrical_kw={e}: baseline={drive(e, 0.05)} mutant={drive(e, 0.1)}")
print(f"RESULT null_delta={sum(int(drive(e, 0.05) != drive(e, 0.1)) for e in (2.0, 5.0))} count")
tail()
