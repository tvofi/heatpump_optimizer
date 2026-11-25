#H Metric: ThermalModel._batch_cop COP for a NaN humidity step (a forecast's unknown step, #21) with a learned humidity-
#H   dependent derate, baseline vs mutant; finiteness; and whether it equals the no-humidity COP the contract names.
#H EXPECTED RESULT nan_equals_none_baseline=1 ; the mutant's value moves (NaN reaches DefrostDerate.factor)
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._batch_cop, line 4458
#H   `if hum_i is not None and not np.isfinite(hum_i):`.
#H Perturbation: key e3a350a3272762f1 GUARD_OFF -> `if False:`, in memory. Direction: finite derated COP -> other / NaN.
#H Null control: finite humidities (50, 90) and None, where the guard is false either way.
#INCLUDE _tm_common.txt
mut = mutant(TM._batch_cop, "            if hum_i is not None and not np.isfinite(hum_i):", "            if False:")
d = derate(lambda i, j: (0.9, 0.6)[min(j, 1)])
for amb in (None, 80.0):
    model = TM(tm.ThermalParameters(two_zone_enabled=True, defrost_derate=d, ambient_humidity=amb))
    tag = "amb_none" if amb is None else "amb80"
    moved = 0
    for out in (-10.0, -2.0, 0.0, 3.0):
        b, m = batch(model, TM._batch_cop, out, float("nan"), T_BUF, False), batch(model, mut, out, float("nan"), T_BUF, False)
        moved += not same(b, m)
        if out == -2.0:
            ref = batch(model, TM._batch_cop, out, None, T_BUF, False)
            print(f"RESULT {tag}_nan_baseline={show(b)}")
            print(f"RESULT {tag}_nan_mutant={show(m)}")
            print(f"RESULT {tag}_nan_mutant_finite={int(m[0] == 'ok' and bool(np.all(np.isfinite(m[1]))))}")
            print(f"RESULT {tag}_nan_equals_none_baseline={int(same(b, ref))}")
            print(f"RESULT {tag}_nan_equals_none_mutant={int(same(m, ref))}")
    print(f"RESULT {tag}_nan_moved={moved} count (of 4 outdoor temps)")
    nm = sum(not same(batch(model, TM._batch_cop, o, h, T_BUF, False), batch(model, mut, o, h, T_BUF, False))
             for o in (-10.0, -2.0, 3.0) for h in (None, 50.0, 90.0))
    print(f"RESULT {tag}_null_moved={nm} count (of 9)")
