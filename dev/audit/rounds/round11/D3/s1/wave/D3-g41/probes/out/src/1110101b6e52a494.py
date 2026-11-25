#H Metric: count of inputs on which ThermalModel._batch_cop's COP differs between `carnot_ref > 1e-9` and `>= 1e-9`;
#H   carnot_ref = (ref + 273.15) / max(., 1.0) equals 1e-9 only for ref + 273.15 equal to 1e-9 times the denominator.
#H EXPECTED RESULT moved_inputs=0 count
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._batch_cop, line 4476
#H   `if carnot_ref > 1e-9:`.
#H Perturbation: key 1110101b6e52a494 CMP_BOUND `>` -> `>=`, in memory. Direction if it moved: carnot term applied at the
#H   1e-9 tie.
#H Null control: baseline against itself.
#INCLUDE _tm_common.txt
mut = mutant(TM._batch_cop, "            if carnot_ref > 1e-9:", "            if carnot_ref >= 1e-9:")
tried = moved = 0
refs = (35.0, 20.0, 7.0, 0.0, -273.15, -273.15 + 1e-9, 1e-9 - 273.15, -273.15 - 1e-9, -300.0)
for ref in refs:
    model = TM(tm.ThermalParameters(two_zone_enabled=True, cop_flow_carnot=True, cop_flow_reference_temp=ref))
    for o in OUTS:
        tried += 1
        moved += not same(batch(model, TM._batch_cop, o, None, T_BUF, True), batch(model, mut, o, None, T_BUF, True))
    t_out = 7.0 + 273.15
    cr = (ref + 273.15) / max(ref + 273.15 - t_out, 1.0)
    print(f"RESULT carnot_ref_at_ref{ref!r}={cr!r}")
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved_inputs={moved} count")
