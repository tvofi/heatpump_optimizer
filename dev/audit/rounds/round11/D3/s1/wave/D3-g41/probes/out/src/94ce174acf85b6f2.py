#H Metric: ThermalModel._batch_cop COP for a step with no humidity (hum_i None) when the live ambient humidity is known
#H   (params.ambient_humidity = 90, published by coordinator.py:6812), with a humidity-dependent learned derate;
#H   baseline vs mutant, and parity with the scalar compute_cop(humidity=None).
#H EXPECTED RESULT moved>0: baseline derates at 90 % RH, the mutant at DefrostDerate's dry-bucket centre
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._batch_cop, line 4460
#H   `if hum_i is None:` (-> hum_i = p.ambient_humidity).
#H Perturbation: key 94ce174acf85b6f2 GUARD_OFF `if hum_i is None:` -> `if False:`, in memory. Direction: up (less derate).
#H Null control: ambient_humidity None (fallback is None either way) and finite hum_i.
#INCLUDE _tm_common.txt
mut = mutant(TM._batch_cop, "            if hum_i is None:", "            if False:")
d = derate(lambda i, j: (0.9, 0.6)[min(j, 1)])
for amb in (90.0, None):
    p = tm.ThermalParameters(two_zone_enabled=True, defrost_derate=d, ambient_humidity=amb)
    model = TM(p)
    tag = "amb90" if amb else "amb_none"
    moved = tried = pb = pm = 0
    for out in OUTS:
        b, m = batch(model, TM._batch_cop, out, None, T_BUF, False), batch(model, mut, out, None, T_BUF, False)
        tried += 1; moved += not same(b, m)
        s = TM(p).compute_cop(out, humidity=None)
        pb += not bool(np.all(b[1] == s)); pm += not bool(np.all(m[1] == s))
        if out == -2.0:
            print(f"RESULT {tag}_cop_m2_baseline={show(b)}")
            print(f"RESULT {tag}_cop_m2_mutant={show(m)}")
            print(f"RESULT {tag}_cop_m2_scalar={s!r}")
    print(f"RESULT {tag}_moved={moved} count (of {tried})")
    print(f"RESULT {tag}_parity_breaks_baseline={pb} count")
    print(f"RESULT {tag}_parity_breaks_mutant={pm} count")
    nm = sum(not same(batch(model, TM._batch_cop, o, 50.0, T_BUF, False), batch(model, mut, o, 50.0, T_BUF, False)) for o in OUTS)
    print(f"RESULT {tag}_finite_hum_null_moved={nm} count")
