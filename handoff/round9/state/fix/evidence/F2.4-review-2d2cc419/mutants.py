"""Reviewer's own mutants for R9-F2.4 (not the fixer's mutation_proof.py).
Usage: mutants.py <tree> <id> apply|show  -- applies one textual mutant in place."""
import sys, pathlib
P = "custom_components/heatpump_optimizer/"
MUT = {
 # R1: the owner's batch form takes the per-circuit max again (the design choice the body states)
 "R1": (P+"thermal_model.py", "((space + dhw) > MIN_RUNNING_DRAW_KW)", "(np.maximum(space, dhw) > MIN_RUNNING_DRAW_KW)"),
 # R2: the entity gate reads falsy instead of an explicit False
 "R2": (P+"entity.py", 'if action.get("heat_pump_on") is False:', 'if not action.get("heat_pump_on"):'),
 # R3: the plan floor moves off 0.1
 "R3": (P+"thermal_model.py", "MIN_RUNNING_DRAW_KW = 0.1", "MIN_RUNNING_DRAW_KW = 0.2"),
 # R4: the action fallback drops the DHW circuit
 "R4": (P+"optimizer.py", "else planned_draw_runs(power, dhw_power_at_i)", "else planned_draw_runs(power)"),
 # R5: count_compressor_starts default returns to a literal that differs from the owner
 "R5": (P+"optimizer.py", "power: np.ndarray, threshold: float = MIN_RUNNING_DRAW_KW", "power: np.ndarray, threshold: float = 0.2"),
 # R6: the scalar form uses >= (boundary)
 "R6": (P+"thermal_model.py", "return (float(space_kw) + float(dhw_kw)) > MIN_RUNNING_DRAW_KW", "return (float(space_kw) + float(dhw_kw)) >= MIN_RUNNING_DRAW_KW"),
 # R7: the arbiter's ledger reads the plan floor instead of the meter threshold
 "R7": (P+"pump_arbiter.py", "return on_threshold_kw(coord._thermal_model.params)", "return 0.1"),
 # R8: the action's space band reads the combined draw
 "R8": (P+"optimizer.py", "space_on = planned_draw_runs(power)", "space_on = planned_draw_runs(power, dhw_power_at_i)"),
}
tree, mid, act = sys.argv[1], sys.argv[2], sys.argv[3]
f, old, new = MUT[mid]
p = pathlib.Path(tree, f); s = p.read_text()
assert s.count(old) == 1, (mid, s.count(old))
if act == "apply":
    p.write_text(s.replace(old, new)); print("applied", mid, f)
