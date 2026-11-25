#H Metric: count of inputs on which ThermalModel._batch_cop's COP differs between `T_buf > ref` and `T_buf >= ref`,
#H   with tanks exactly at, and one ulp around, cop_flow_reference_temp.
#H EXPECTED RESULT moved_inputs=0 count (at T_buf == ref, carnot_flow == carnot_ref, so max(0.25, 1.0) == 1.0)
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._batch_cop, line 4482 `T_buf > ref,`.
#H Perturbation: key d6023ebc83ac4317 CMP_BOUND `T_buf > ref,` -> `T_buf >= ref,`, in memory. Direction if it moved: the
#H   tie tank's multiplier 1.0 -> carnot_flow / carnot_ref.
#H Null control: baseline against itself.
#INCLUDE _tm_common.txt
mut = mutant(TM._batch_cop, "                    T_buf > ref,", "                    T_buf >= ref,")
tried = moved = 0
for ref in (35.0, 20.0, 50.0, 7.0, 7.3):
    tb = np.array([ref, np.nextafter(ref, -np.inf), np.nextafter(ref, np.inf), ref - 10.0, ref + 10.0])
    model = TM(tm.ThermalParameters(two_zone_enabled=True, cop_flow_carnot=True, cop_flow_reference_temp=ref))
    for o in OUTS:
        tried += 1
        moved += not same(batch(model, TM._batch_cop, o, None, tb, True), batch(model, mut, o, None, tb, True))
print(f"RESULT inputs_tried={tried} count (each a 5-tank row with the tie)")
print(f"RESULT moved_inputs={moved} count")
