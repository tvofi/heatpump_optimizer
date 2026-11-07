import sys, pathlib
P = "custom_components/heatpump_optimizer/"
M = {
 "A_if_measured_true": (P+"coordinator.py", "        if measured:\n            self._measured_cop.record", "        if True:\n            self._measured_cop.record"),
 "B_cop_sample_none_false": (P+"thermal_model.py", "return None if self.measured_heat and not self.heat_counter else False", "return False"),
 "C_id_rule_off": (P+"thermal_model.py", "    return const.ESTIMATE_ID_MARK in str(entity_id or \"\").lower()", "    return False"),
 "D_power_side_only_heat": (P+"thermal_model.py", "and not (self.heat_estimated or self.power_estimated)", "and not self.heat_estimated"),
 "E_heat_side_only_power": (P+"thermal_model.py", "and not (self.heat_estimated or self.power_estimated)", "and not self.power_estimated"),
 "F_loader_old_key": (P+"coordinator.py", "raw_baseline = stored.get(_COP_BASELINE_KEY)", "raw_baseline = stored.get(_COP_BASELINE_KEY, stored.get(\"cop_baseline\"))"),
 "G_measured_cop_ungated": (P+"coordinator.py", "MeasuredCop.from_dict(stored.get(\"measured_cop\") if _COP_BASELINE_KEY in stored else None)", "MeasuredCop.from_dict(stored.get(\"measured_cop\"))"),
 "H_machine_score_ungated": (P+"coordinator.py", "    if not measurable:\n        return None, \"cop_unmeasurable\", []\n", ""),
 "I_dhw_coverage_off": (P+"thermal_model.py", "            and (self.heat_sees_dhw or not dhw)\n", ""),
 "J_cusum_old_key": (P+"coordinator.py", "self._cop_health_cusum.load(stored.get(_COP_HEALTH_CUSUM_KEY))", "self._cop_health_cusum.load(stored.get(_COP_HEALTH_CUSUM_KEY, stored.get(\"cop_health_cusum\")))"),
 "K_obs_estimated_as_metered": (P+"accuracy.py", "return COP_ESTIMATED if estimated else COP_HEAT_METERED", "return COP_HEAT_METERED"),
 "L_counter_power_estimate": (P+"thermal_model.py", "power_estimated=not cfg.get(const.CONF_HEAT_ENERGY_ENTITY) and _estimated(", "power_estimated=_estimated("),
}
name, root = sys.argv[1], pathlib.Path(sys.argv[2])
f, old, new = M[name]
p = root / f; t = p.read_text()
assert t.count(old) == 1, (name, t.count(old))
p.write_text(t.replace(old, new)); print("applied", name)
