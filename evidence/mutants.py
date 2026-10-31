import sys,pathlib
C='custom_components/heatpump_optimizer/'
M={
'G1':(C+'dhw_planner.py',"plan[j] += added_power_for_heat_per_cop_kw(params, plan[j], take / (cop * dt))","plan[j] += take / (cop * dt)"),
'G2':(C+'dhw_planner.py',"""spare_thermal_kwh = (
                    heat_per_cop_kw(params, p_dhw_max) - heat_per_cop_kw(params, plan[j])
                ) * cop * dt""","spare_thermal_kwh = (p_dhw_max - plan[j]) * cop * dt"),
'B1':(C+'dhw_planner.py',"""baseline_dhw = np.full(
            n_steps, power_for_heat_per_cop_kw(p, (baseline_draw + standby_loss) / cop_dhw))""","baseline_dhw = np.full(n_steps, (baseline_draw + standby_loss) / cop_dhw)"),
'L1':(C+'dhw_planner.py',"rise = delivered_heat_kw(params, cop, p_dhw_run) * dt / c_dhw","rise = p_dhw_run * cop * dt / c_dhw"),
'R1':(C+'dhw_planner.py',"""needed = added_power_for_heat_per_cop_kw(
                    params, plan[j], float(deficit[b]) * c_dhw / max(dt * cop_j, 1e-6))""","needed = float(deficit[b]) * c_dhw / max(dt * cop_j, 1e-6)"),
'R2':(C+'dhw_planner.py',"""room_kw = added_power_for_heat_per_cop_kw(
                    params, plan[j], float(room_c[j_local]) * c_dhw / max(dt * cop_room, 1e-6))""","room_kw = float(room_c[j_local]) * c_dhw / max(dt * cop_room, 1e-6)"),
'C1':(C+'coordinator.py',"cap_i = float(np.clip(power_for_heat_per_cop_kw(model.params, float(entry[0]) / cop_i), floor, p_max))","cap_i = float(np.clip(float(entry[0]) / cop_i, floor, p_max))"),
'T1':(C+'optimizer.py',"""allowed = float(schedule[i]) + added_power_for_heat_per_cop_kw(
                self.model.params, float(schedule[i]), -float(refused[i]) / max(cop_i, 1e-6))""","allowed = float(schedule[i]) - float(refused[i]) / max(cop_i, 1e-6)"),
'V1':(C+'battery.py',"return max(self.cop, 0.1) * self.charge_heat_per_cop_kw","return self.charge_power_kw * max(self.cop, 0.1)"),
'A0':(C+'thermal_model.py',"""    if not params.cop_partload_derate:
        return heat_per_cop
    return power_for_heat_per_cop_kw(
        params, heat_per_cop_kw(params, power_kw) + heat_per_cop) - power_kw""","    return heat_per_cop"),
}
f,a,b=M[sys.argv[1]]; p=pathlib.Path(f); s=p.read_text(); assert s.count(a)==1,(sys.argv[1],s.count(a)); p.write_text(s.replace(a,b)); print('mutated',sys.argv[1],f)
