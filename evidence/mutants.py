# Reviewer's own mutants (not the fixer's): name, file, old, new
M = [
 ("r1_bandfields_guard", "coordinator.py", '    if band.source == "configured":\n        return {}', '    if False:\n        return {}'),
 ("r2_whatif_noband", "coordinator.py", "**_band_fields(band or _solve_band(self._accuracy.draw, ctx._thermal_params, ctx._config)),", "**_band_fields(band) if band else {},"),
 ("r3_stamp", "coordinator.py", "self._optimization_result = replace(result, solve_band=record.band.as_dict())", "self._optimization_result = result"),
 ("r4_edge", "draw_range.py", "if learned >= (1.0 - AGREE_TOLERANCE) * cfg_max:", "if learned > (1.0 - AGREE_TOLERANCE) * cfg_max:"),
 ("r5_warmclip", "optimizer.py", "return (np.clip(np.asarray(prev, dtype=float), 0.0, self.model.params.max_electrical_power),)", "return (np.asarray(prev, dtype=float),)"),
 ("r6_arbiter_read", "pump_arbiter.py", "    if band and _experiment_kw(inp) is None:\n        return band[\"planned_min_kw\"], band[\"planned_max_kw\"]", "    pass"),
 ("r7_min_clamp", "draw_range.py", 'cfg_max, learned, min(cfg_min, learned), "ceiling_probe",', 'cfg_max, learned, cfg_min, "ceiling_probe",'),
 ("r8_publish", "coordinator.py", '"pump_max_power": getattr(self._optimization_result, "solve_band", None) or None,', ''),
 ("r9_echo", "draw_range.py", '    if cap.plan_writes_power():\n        return configured("plan_writes_power")\n', ''),
 ("r10_samples", "draw_range.py", 'return configured("lapsed" if samples >= CEILING_MIN_SAMPLES else "awaiting_probe")', 'return configured("awaiting_probe")'),
]
