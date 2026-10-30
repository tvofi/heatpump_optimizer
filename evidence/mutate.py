import sys
M = {
 "M0": ("custom_components/heatpump_optimizer/thermal_model.py",
        "    if not d or band <= 0.0:\n        return heat_per_cop\n    p_min", "    if True:\n        return heat_per_cop\n    p_min"),
 "M1": ("custom_components/heatpump_optimizer/dhw_planner.py",
        "power_for_heat_per_cop_kw(params, energy / (cop * dt))", "energy / (cop * dt)"),
 "M2": ("custom_components/heatpump_optimizer/dhw_planner.py",
        "cop * heat_per_cop_kw(params, p_dhw_max) * dt", "p_dhw_max * cop * dt"),
 "M3": ("custom_components/heatpump_optimizer/dhw_planner.py",
        "allowed = power_for_heat_per_cop_kw(\n                params, (headroom_c * capacity / dt + q_draw + q_loss) / cop\n            )",
        "allowed = (headroom_c * capacity / dt + q_draw + q_loss) / cop"),
 "M4": ("custom_components/heatpump_optimizer/dhw_planner.py",
        "dhw_power_thermal=delivered_heat_kw(params, cop, plan[i])", "dhw_power_thermal=cop * plan[i]"),
 "M5": ("custom_components/heatpump_optimizer/optimizer.py",
        "power_for_heat_per_cop_kw(p, required_thermal / cop)", "required_thermal / cop"),
 "M6": ("custom_components/heatpump_optimizer/coordinator.py",
        "mean_price * power_for_heat_per_cop_kw(\n                params, (standby_kwh + draw_day_kwh) / cop, hours=24.0)",
        "(standby_kwh + draw_day_kwh) / cop * mean_price"),
}
f, old, new = M[sys.argv[1]]
s = open(f).read(); assert s.count(old) == 1, (sys.argv[1], s.count(old)); open(f, "w").write(s.replace(old, new))
print("applied", sys.argv[1], f)
