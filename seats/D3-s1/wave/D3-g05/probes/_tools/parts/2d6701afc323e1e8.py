OLD, NEW = "if 0 < idx < len(trajectory):", "if 0 <= idx < len(trajectory):"
MUT = mutant_method("_file_dhw_lead_predictions", OLD, NEW)
from custom_components.heatpump_optimizer.accuracy import LEAD_BUCKETS
c = coord()
dt_prod = max(c._opt_config.time_step_minutes, 1.0) / 60.0   # what _file_lead_predictions passes
moved_prod = 0
for n in range(0, 201):
    moved_prod += int(counted(CLS._file_dhw_lead_predictions, [50.0] * n, dt_prod) != counted(MUT, [50.0] * n, dt_prod))
print(f"RESULT production_dt_h={dt_prod} min_idx={min(int(round(l / dt_prod)) for l in LEAD_BUCKETS)}")
print(f"RESULT moved_lengths_at_production_dt={moved_prod} of 201 count")
# positive control off the production grid: a 3 h step rounds the 1 h lead to idx 0
b, m = counted(CLS._file_dhw_lead_predictions, [50.0] * 97, 3.0), counted(MUT, [50.0] * 97, 3.0)
print(f"RESULT offgrid_dt3h baseline_leads={b[0]} mutant_leads={m[0]} count")
room_len, dhw_len = solved_lengths()
print(f"RESULT solved_trajectory_lengths room={room_len} dhw={dhw_len} count")
tail()
