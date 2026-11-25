#H Metric: ThermalModel._batch_cop COP for an UNthrottled step (flow_carnot_eligible False) with cop_flow_carnot on,
#H   baseline vs mutant; parity breaks with the scalar compute_cop(flow_temp=None), which an unthrottled scalar step passes.
#H EXPECTED RESULT moved>0: the mutant applies the Carnot lift cost to tanks above cop_flow_reference_temp (35 C)
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._batch_cop, line 4463
#H   `if flow_carnot_eligible and p.cop_flow_carnot:`.
#H Perturbation: key 898d741cf6142efb BOOLOP `and` -> `or`, in memory. Direction: down (COP lowered for hot tanks).
#H Null control: eligible True (both arms enter the branch) and cop_flow_carnot False with eligible False (neither does
#H   under baseline; the mutant does not either since `False or False`).
#INCLUDE _tm_common.txt
mut = mutant(TM._batch_cop, "        if flow_carnot_eligible and p.cop_flow_carnot:",
             "        if flow_carnot_eligible or p.cop_flow_carnot:")
p = tm.ThermalParameters(two_zone_enabled=True, cop_flow_carnot=True)
model = TM(p)
moved = tried = pb = pm = 0
for out in OUTS:
    b, m = batch(model, TM._batch_cop, out, None, T_BUF, False), batch(model, mut, out, None, T_BUF, False)
    tried += 1; moved += not same(b, m)
    s = TM(p).compute_cop(out, flow_temp=None)
    pb += not bool(np.all(b[1] == s)); pm += not bool(np.all(m[1] == s))
    if out == 0.0:
        print(f"RESULT cop_out0_baseline={show(b)}")
        print(f"RESULT cop_out0_mutant={show(m)}")
        print(f"RESULT cop_out0_scalar_unthrottled={s!r}")
print(f"RESULT moved={moved} count (of {tried} outdoor temps x 5 tanks)")
print(f"RESULT parity_breaks_baseline={pb} count")
print(f"RESULT parity_breaks_mutant={pm} count")
n1 = sum(not same(batch(model, TM._batch_cop, o, None, T_BUF, True), batch(model, mut, o, None, T_BUF, True)) for o in OUTS)
m0 = TM(tm.ThermalParameters(two_zone_enabled=True, cop_flow_carnot=False))
n2 = sum(not same(batch(m0, TM._batch_cop, o, None, T_BUF, False), batch(m0, mut, o, None, T_BUF, False)) for o in OUTS)
print(f"RESULT null_eligible_moved={n1} count")
print(f"RESULT null_carnot_off_moved={n2} count")
n3 = sum(not same(batch(m0, TM._batch_cop, o, None, T_BUF, True), batch(m0, mut, o, None, T_BUF, True)) for o in OUTS)
print(f"RESULT throttled_carnot_off_moved={n3} count (eligible True, cop_flow_carnot False: the mutant enters the branch)")
