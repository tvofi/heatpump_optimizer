import sys, pathlib
root = pathlib.Path(sys.argv[1]); name = sys.argv[2]
D = "custom_components/heatpump_optimizer/drift.py"; C = "custom_components/heatpump_optimizer/coordinator.py"
M = {
 "M1": (D, "departure = self._clipped(value - float(theta @ u))", "departure = self._clipped(value)"),
 "M2": (C, """vent_changed = self._vent_cusum.update(now, float(residual), (
            previous_power * dt_h, (previous_state.solar_radiation or 0.0) * dt_h / 1000.0))""", "vent_changed = self._vent_cusum.update(now, float(residual), ())"),
 "M3": (D, "self.reference = [self._clipped(value)] + [0.0] * (k - 1)", "self.reference = [value] + [0.0] * (k - 1)"),
 "M4": (D, "        cov = cov * np.outer(shrink, shrink)\n", ""),
 "M5": (C, "            reference_hours=VENT_CUSUM_REFERENCE_HOURS,\n", ""),
 "M6": (D, "return min(max(value, -self.clip), self.clip)", "return max(value, -self.clip)"),
 "M6b": (D, "return min(max(value, -self.clip), self.clip)", "return min(value, self.clip)"),
 "M7": (D, "REFERENCE_PRIOR_COV = 1.0", "REFERENCE_PRIOR_COV = 2.0"),
 "M9": (C, "            clip=VENT_CUSUM_CLIP_C,\n            reference_hours", "            reference_hours"),
 "M10": (C, "(previous_state.solar_radiation or 0.0) * dt_h / 1000.0))", "0.0))"),
 "M11": (C, "previous_power * dt_h, (previous_state", "0.0, (previous_state"),
}
f, old, new = M[name]; p = root / f; s = p.read_text()
assert s.count(old) == 1, (name, s.count(old)); p.write_text(s.replace(old, new)); print("applied", name)
