import sys, json, pathlib
CO="custom_components/heatpump_optimizer/coordinator.py"
SE="custom_components/heatpump_optimizer/sensor.py"
CA="custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
M={
# the six ledger sites (a9099faf3)
"L1_watched_cmp":(CO,"int(entry[1]) >= COP_BASELINE_MIN_SAMPLES\n    )","int(entry[1]) > COP_BASELINE_MIN_SAMPLES\n    )"),
"L2_refit_cmp":(CO,"return abs(float(fitted) - scale) > band * scale","return abs(float(fitted) - scale) >= band * scale"),
"L3_env_loss_cmp":(CO,"if loss <= 0.0 or params.room_thermal_mass <= 0:","if loss < 0.0 or params.room_thermal_mass <= 0:"),
"L4_env_mass_cmp":(CO,"if loss <= 0.0 or params.room_thermal_mass <= 0:","if loss <= 0.0 or params.room_thermal_mass < 0:"),
"L5_env_guard_off":(CO,"    if loss <= 0.0 or params.room_thermal_mass <= 0:\n","    if False:\n"),
"L6_machine_clamp":(CO,"float(np.clip(cusum_stat / COP_HEALTH_THRESHOLD, 0.0, 1.0))","float((cusum_stat / COP_HEALTH_THRESHOLD))"),
# my own
"R1_loss_configured":(CO,"loss = _effective_house_heat_loss(params, scale)","loss = round(params.heat_loss_coefficient * scale, 4)"),
"R2_learned_any_sample":(CO,'"house_heat_loss_learned": house_loss_converged(\n                self._house_heat_loss_samples\n            ),','"house_heat_loss_learned": self._house_heat_loss_samples > 0,'),
"R3_precedence_swap":(CO,'    if not house_loss_converged(samples):\n        return None, "heat_loss_learning"\n    if _refit_disagrees(advice, scale):\n        return None, "heat_loss_refit_disagrees"\n','    if _refit_disagrees(advice, scale):\n        return None, "heat_loss_refit_disagrees"\n    if not house_loss_converged(samples):\n        return None, "heat_loss_learning"\n'),
"R4_band_on_fitted":(CO,"> band * scale","> band * float(fitted)"),
"R5_reason_for_grades":(CO,"reasons = {key: why for key, (_grade, why) in parts.items() if why is not None}","reasons = {key: (why or \"graded\") for key, (_grade, why) in parts.items()}"),
"R6_adopt_listeners":(CO,"    await coord.async_request_refresh()\n    return True","    coord.async_update_listeners()\n    return True"),
"R7_restore_listeners":(CO,"await self.async_request_refresh()  # re-plan","self.async_update_listeners()  # re-plan"),
"R8_op_reason_const":(CO,'return "free_price_reset" if free >= SCORE_FREE_SPAN_RESET else "no_scored_day"','return "no_scored_day"'),
"R9_convergence_half":(CO,"_HOUSE_LOSS_CONVERGED_CONFIDENCE = house_loss_confidence(round(1.0 / HOUSE_LOSS_ALPHA))","_HOUSE_LOSS_CONVERGED_CONFIDENCE = house_loss_confidence(round(0.5 / HOUSE_LOSS_ALPHA))"),
"R10_watched_finite_drop":(CO,"if np.isfinite(entry[1]) and int(entry[1])","if int(entry[1])"),
"R11_sensor_fallback_none":(SE,'        scale = _as_float(data.get("house_heat_loss_scale"))\n        return {\n            "drift_alarm": False,\n            "current_scale": None if scale is None else round(scale, 3),','        scale = _as_float(data.get("house_heat_loss_scale"))\n        return {\n            "drift_alarm": False,\n            "current_scale": None,'),
"R12_refit_none_disagrees":(CO,"    if fitted is None:\n        return False\n","    if fitted is None:\n        return True\n"),
"R13_scores_fresh_advice":(CO,'"scores": self._scores_view(advice),','"scores": self._scores_view({}),'),
"C1_readnumber_null":(CA,'  if (raw === null || raw === undefined || raw === "") return null;\n  const n = Number(raw);\n  return Number.isFinite(n) ? n : null;\n}\n\n/** The score sensor','  const n = Number(raw);\n  return Number.isFinite(n) ? n : null;\n}\n\n/** The score sensor'),
"C2_healthwaiting_unavail":(CA,'return st.state === "unavailable" || (st.state === "unknown" && !!(st.attributes || {}).waiting_for);','return st.state === "unavailable";'),
"C3_reason_text_generic":(CA,"reason: value === null ? scoreReasonText(reasons[key]) : null","reason: value === null ? L(\"score.no_evidence\") : null"),
}
name, root = sys.argv[1], sys.argv[2]
f, old, new = M[name]
p = pathlib.Path(root)/f
t = p.read_text()
n = t.count(old)
assert n == 1, (name, n)
p.write_text(t.replace(old, new))
print("applied", name, f)
