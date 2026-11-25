#H Metric: ThermalModel.compute_cop / _cop_law COP at each outdoor temperature, baseline vs mutant; count of outdoor
#H   temperatures where they differ; and parity breaks of the batch twin _batch_cop against the mutated scalar.
#H EXPECTED RESULT cop_out30_mutant > cop_out30_baseline (factor 1.575 unclamped above cop_reference_temp + 20 K)
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._cop_law, line 3328
#H   `cop = self.params.cop_nominal * min(factor, 1.5) * self.params.cop_scale`; reached by compute_cop (line 3301) and the
#H   DHW COP (line 3457), i.e. every scalar simulate_step.
#H Perturbation: key a6cebb125b72f083 CLAMP_DROP `min(factor, 1.5)` -> `(factor)`, in memory, patched onto ThermalModel
#H   (a fresh model per arm, so no memo crosses arms). Direction: up.
#H Null control: outdoor <= 27 C, where the clamp is inert.
#INCLUDE _tm_common.txt
mut = mutant(TM._cop_law, "        cop = self.params.cop_nominal * min(factor, 1.5) * self.params.cop_scale",
             "        cop = self.params.cop_nominal * (factor) * self.params.cop_scale")
tried = moved = null_moved = pm = 0
for out in OUTS:
    b = outcome(TM(tm.ThermalParameters(two_zone_enabled=True)).compute_cop, out)
    with mock.patch.object(TM, "_cop_law", mut):
        mm = TM(tm.ThermalParameters(two_zone_enabled=True))
        m = outcome(mm.compute_cop, out)
        bt = outcome(mm._batch_cop, out, None, T_BUF, False)
    tried += 1
    moved += not same(b, m)
    if out <= 27.0:
        null_moved += not same(b, m)
    pm += not bool(np.all(bt[1] == m[1]))
    if out == 30.0:
        print(f"RESULT cop_out30_baseline={show(b)}")
        print(f"RESULT cop_out30_mutant={show(m)}")
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT null_moved={null_moved} count (outdoor <= 27 C)")
print(f"RESULT batch_scalar_parity_breaks_mutant={pm} count")
