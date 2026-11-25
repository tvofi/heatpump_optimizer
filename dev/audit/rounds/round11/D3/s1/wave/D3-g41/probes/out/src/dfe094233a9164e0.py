#H Metric: ThermalModel._batch_cop COP with a learned defrost derate (inferred factor 0.7, trusted) at -2 C / 90 % RH,
#H   baseline vs mutant; count of (outdoor, humidity) inputs that differ; parity breaks against the scalar compute_cop.
#H EXPECTED RESULT cop_m2_h90_mutant = cop_m2_h90_baseline / 0.7 (derate never applied)
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._batch_cop, line 4455
#H   `if derate is not None:`.
#H Perturbation: key dfe094233a9164e0 GUARD_OFF `if derate is not None:` -> `if False:`, in memory. Direction: up.
#H Null control: defrost_derate None (guard false either way): null_moved must be 0.
#INCLUDE _tm_common.txt
mut = mutant(TM._batch_cop, "        if derate is not None:", "        if False:")
d = derate(lambda i, j: 0.7)
print(f"RESULT derate_factor_m2_h90={d.factor(-2.0, 90.0)!r}")
model = TM(tm.ThermalParameters(two_zone_enabled=True, defrost_derate=d))
nullm = TM(tm.ThermalParameters(two_zone_enabled=True))
tried = moved = null_moved = pb = pm = 0
for out in OUTS:
    for hum in (None, 50.0, 90.0):
        b, m = batch(model, TM._batch_cop, out, hum, T_BUF, False), batch(model, mut, out, hum, T_BUF, False)
        tried += 1; moved += not same(b, m)
        null_moved += not same(batch(nullm, TM._batch_cop, out, hum, T_BUF, False), batch(nullm, mut, out, hum, T_BUF, False))
        s = TM(tm.ThermalParameters(two_zone_enabled=True, defrost_derate=d)).compute_cop(out, humidity=hum)
        pb += not bool(np.all(b[1] == s)); pm += not bool(np.all(m[1] == s))
        if out == -2.0 and hum == 90.0:
            print(f"RESULT cop_m2_h90_baseline={show(b)}")
            print(f"RESULT cop_m2_h90_mutant={show(m)}")
            print(f"RESULT cop_m2_h90_scalar={s!r}")
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT null_moved={null_moved} count")
print(f"RESULT parity_breaks_baseline={pb} count")
print(f"RESULT parity_breaks_mutant={pm} count")
