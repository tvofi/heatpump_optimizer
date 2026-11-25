OLD, NEW = "if 0 < idx < len(trajectory):", "if 0 < idx <= len(trajectory):"
MUT = mutant_method("_file_dhw_lead_predictions", OLD, NEW)
from custom_components.heatpump_optimizer.accuracy import LEAD_BUCKETS
c = coord()
dt_prod = max(c._opt_config.time_step_minutes, 1.0) / 60.0
moved = []
for n in range(0, 201):
    def run(fn):
        try:
            return counted(fn, [50.0] * n, dt_prod)
        except Exception as e:  # noqa: BLE001
            return f"raised {type(e).__name__}"
    if run(CLS._file_dhw_lead_predictions) != run(MUT):
        moved.append(n)
print(f"RESULT lead_idx={[int(round(l / dt_prod)) for l in LEAD_BUCKETS]}")
print(f"RESULT moved_lengths={moved} (mutant raises IndexError at len == a lead idx)")
room_len, dhw_len = solved_lengths()
print(f"RESULT solved_trajectory_lengths room={room_len} dhw={dhw_len} count")
b, m = counted(CLS._file_dhw_lead_predictions, [50.0] * dhw_len, dt_prod), counted(MUT, [50.0] * dhw_len, dt_prod)
print(f"RESULT at_solved_length baseline_leads={b[0]} mutant_leads={m[0]} count")
tail()
