#H Metric: count of (cop_flow_reference_temp, outdoor, tank) inputs on which ThermalModel._batch_cop's COP differs, split
#H   into the production reference (cop_flow_reference_temp 35 C and cop_reference_temp 7 C: ThermalParameters defaults
#H   that no config key sets) and off-production references within 1 K of, or below, the clipped outdoor temperature.
#H EXPECTED RESULT production_moved=0 count (ref + 273.15 - t_out >= 28 K there, so max(., 1.0) is inert)
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._batch_cop, line 4475
#H   `carnot_ref = (ref + 273.15) / max(ref + 273.15 - t_out, 1.0)`.
#H Perturbation: key 29065b9e48071934 CLAMP_DROP `max(ref + 273.15 - t_out, 1.0)` -> `(ref + 273.15 - t_out)`, in memory.
#H   Direction: carnot_ref up (ref within 1 K above t_out) or negative (ref below t_out), off production only.
#H Null control: the production reference, which is the null by construction of the claim.
#INCLUDE _tm_common.txt
mut = mutant(TM._batch_cop, "            carnot_ref = (ref + 273.15) / max(ref + 273.15 - t_out, 1.0)",
             "            carnot_ref = (ref + 273.15) / (ref + 273.15 - t_out)")
res = {}
for ref in (35.0, 20.0, 8.0, 7.5, 7.0, 5.0):
    model = TM(tm.ThermalParameters(two_zone_enabled=True, cop_flow_carnot=True, cop_flow_reference_temp=ref))
    mv = sum(not same(batch(model, TM._batch_cop, o, None, T_BUF, True), batch(model, mut, o, None, T_BUF, True))
             for o in OUTS)
    res[ref] = mv
    print(f"RESULT moved_ref{ref:g}={mv} count (of {len(OUTS)})")
print(f"RESULT production_moved={res[35.0]} count")
print(f"RESULT inputs_tried={6 * len(OUTS)} count")
d = tm.ThermalParameters()
print(f"RESULT defaults_cop_flow_reference_temp={d.cop_flow_reference_temp} C, cop_reference_temp={d.cop_reference_temp} C")
