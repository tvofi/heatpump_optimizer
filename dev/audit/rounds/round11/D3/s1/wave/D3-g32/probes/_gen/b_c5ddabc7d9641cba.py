mut = mutate(SID, "_size_step_power", "        cop = max(cop, 0.1)", "        cop = (cop)")
low = [(p, c, 21.0, o) for p in (3.0, 6.0, 12.0, 40.0, 80.0, 160.0) for c in (0.0, 0.05, 0.09, -1.0) for o in (2.0, 12.0, 16.0, 18.0)]
for a in low[48:54]:
    print(f"RESULT sample_{a}: baseline={call(SID._size_step_power, *a, HOUSES['light'])} mutant={call(mut, *a, HOUSES['light'])}")
moved, n = scan(mut, args=low)
print(f"RESULT low_cop_inputs_moved={moved}/{n} count")
nm, nn = scan(mut, show=0)
print(f"RESULT null_cop_ge_0.1_moved={nm}/{nn} count")
# reach: the coordinator's only call passes cop = ThermalModel.compute_cop(outdoor), whose COP law floors at 1.0
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
tm_ = ThermalModel(ThermalParameters())
cops = [float(tm_.compute_cop(float(t))) for t in range(-40, 41)]
print(f"RESULT production_cop_min={min(cops):.3f} over outdoor -40..40 C  (the floor removed only acts below 0.1)")
tail()
