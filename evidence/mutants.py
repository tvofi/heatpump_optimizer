# Reviewer's targeted mutants: (id, file, old, new)
O = "custom_components/heatpump_optimizer/optimizer.py"; L = "custom_components/heatpump_optimizer/ledger.py"
M = [
 ("M1-stored-zero", O, '"stored_kw_th": (after - before) / dt,', '"stored_kw_th": 0.0,'),
 ("M2-zone-rooms", O, "        zone = lowers\n", "        zone = rooms\n"),
 ("M3-delivered-start", O, "delivered = 0.5 * (zone[i] + zone[j])", "delivered = zone[i]"),
 ("M4-comfort-noclip", O, "(d_t if d_t > 0.0 else 0.0) - (d_d if d_d > 0.0 else 0.0)", "d_t - d_d"),
 ("M5-cop-floor-off", O, "        if cop < 1e-3:\n            cop = 1e-3\n", ""),
 ("M6-terms-2z-swap-u", O, "    return u_lower, q_solar_lower, q_int_lower", "    return u_lower, q_solar_lower, 0.0"),
 ("M7-terms-1z-solar", O, "return u_eff, p.internal_gains, model.compute_solar_gain(solar_radiation)", "return u_eff, p.internal_gains, 0.0"),
 ("M8-stored-cop-mul", L, 'self.line(key, SAVINGS_STORED_LINE)["kwh"] / cop', 'self.line(key, SAVINGS_STORED_LINE)["kwh"] * cop'),
 ("M9-stored-unscaled", L, "stored_sek = 0.0 if cop is None or actual[\"kwh\"] <= 0 else scale * (", "stored_sek = 0.0 if cop is None or actual[\"kwh\"] <= 0 else 1.0 * ("),
 ("M10-comfort-unscaled", L, 'comfort_sek = self.line(key, SAVINGS_COMFORT_LINE)["sek"] * scale', 'comfort_sek = self.line(key, SAVINGS_COMFORT_LINE)["sek"]'),
 ("M11-cop-floor-meta", L, "max(float(steady_cop), 1e-3)", "float(steady_cop)"),
 ("M12-buffer-off", O, "        if bufs is not None:\n            state.buffer_tank_temperature = bufs[j]\n", ""),
 ("M13-sched-baseline-off", O, '            step["baseline_kw"] = baseline[i]\n', "            pass\n"),
 ("M14-floor-target-old-order", O, "    return u * (target - outdoor_temp) - a - b", "    return u * (target - outdoor_temp) - b - a"),
]
