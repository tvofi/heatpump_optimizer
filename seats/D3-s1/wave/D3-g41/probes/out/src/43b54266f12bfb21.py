#H Metric: (a) count of (outdoor, tank) inputs on which ThermalModel._batch_cop's COP differs between baseline and mutant;
#H   (b) count of outdoor temperatures where the mutant batch COP breaks bitwise parity with the scalar compute_cop
#H   (throttled False: the scalar takes flow_temp None); (c) the COP at 30 C outdoor, both arms.
#H EXPECTED RESULT cop_out30_baseline=<nominal*1.5*scale> ; cop_out30_mutant larger (factor 1.575 unclamped)
#H EXPECTED RESULT parity_breaks_mutant>0 count, parity_breaks_baseline=0 count
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._batch_cop, line 4453
#H   `cop: float | np.ndarray = p.cop_nominal * min(factor, 1.5) * p.cop_scale`; callers simulate_trajectory_batch
#H   (thermal_model.py:4650, :4785).
#H Perturbation: key 43b54266f12bfb21 CLAMP_DROP `min(factor, 1.5)` -> `(factor)`, in memory, patched onto ThermalModel.
#H   Direction: up (COP above the 1.5x ceiling once outdoor > cop_reference_temp + 20 K).
#H Null control: outdoor <= 27 C (factor <= 1.5), where the clamp is inert.
#INCLUDE _tm_common.txt
mut = mutant(TM._batch_cop, "        cop: float | np.ndarray = p.cop_nominal * min(factor, 1.5) * p.cop_scale",
             "        cop: float | np.ndarray = p.cop_nominal * (factor) * p.cop_scale")
model = TM(tm.ThermalParameters(two_zone_enabled=True))
base = TM._batch_cop
tried = moved = null_moved = pb = pm = 0
for out in OUTS:
    b, m = batch(model, base, out, None, T_BUF, False), batch(model, mut, out, None, T_BUF, False)
    tried += 1
    moved += not same(b, m)
    if out <= 27.0:
        null_moved += not same(b, m)
    s = TM(tm.ThermalParameters(two_zone_enabled=True)).compute_cop(out)
    pb += not bool(np.all(b[1] == s)); pm += not bool(np.all(m[1] == s))
    if out == 30.0:
        print(f"RESULT cop_out30_baseline={show(b)}")
        print(f"RESULT cop_out30_mutant={show(m)}")
        print(f"RESULT cop_out30_scalar={s!r}")
print(f"RESULT inputs_tried={tried} count (outdoor temps x 5 tank temps each)")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT null_moved={null_moved} count (outdoor <= 27 C)")
print(f"RESULT parity_breaks_baseline={pb} count")
print(f"RESULT parity_breaks_mutant={pm} count")
