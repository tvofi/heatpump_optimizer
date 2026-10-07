"""Reviewer's step-14 plant (r9c-rev-2025 round 4): re-wrap the three statements
the merge and df9131ab joined, nothing else, and let structure.py measure."""
import pathlib
p = pathlib.Path("/Users/timmalmstrom/hpo-seats/r9c-rev-2025-r4/custom_components/heatpump_optimizer/coordinator.py")
s = p.read_text()
R = [
 ("            await self._dhw_learner.async_set_cooling_rate(float(params[CONF_DHW_COOLING_RATE]))\n",
  "            await self._dhw_learner.async_set_cooling_rate(\n                float(params[CONF_DHW_COOLING_RATE])\n            )\n"),
 ("            ctx._thermal_params.dhw_schedule_enabled = bool(params[CONF_DHW_SCHEDULE_ENABLED])\n",
  "            ctx._thermal_params.dhw_schedule_enabled = bool(\n                params[CONF_DHW_SCHEDULE_ENABLED]\n            )\n"),
]
for a, b in R:
    assert s.count(a) == 1, a[:40]
    s = s.replace(a, b)
p.write_text(s)
