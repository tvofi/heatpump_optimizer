OLD, NEW = "if 0 < idx < len(trajectory):", "if 0 <= idx < len(trajectory):"  # unique in _file_lead_predictions (line 10231)
MUT = mutant_method("_file_lead_predictions", OLD, NEW)
from custom_components.heatpump_optimizer.accuracy import LEAD_BUCKETS
c = coord()
dt_prod = max(c._opt_config.time_step_minutes, 1.0) / 60.0
moved = 0
for n in range(0, 201):
    moved += int(counted(CLS._file_lead_predictions, [21.0] * n, None, room=True)
                 != counted(MUT, [21.0] * n, None, room=True))
print(f"RESULT production_dt_h={dt_prod} min_idx={min(int(round(l / dt_prod)) for l in LEAD_BUCKETS)}")
print(f"RESULT moved_lengths_at_production_dt={moved} of 201 count")
# positive control off the production grid: a 180-min step rounds the 1 h lead to idx 0
def offgrid(fn):
    cc = lead_coord()
    cc._opt_config.time_step_minutes = 180.0
    leads = []
    with mock.patch.object(cc._accuracy, "note_lead_prediction", lambda *a: leads.append(a)), \
         mock.patch.object(cc._accuracy, "note_promise", lambda *a: None), \
         mock.patch.object(cc, "_file_dhw_lead_predictions", lambda *a: None):
        fn(cc, replace(solved(), room_temp_trajectory=[21.0] * 97, upper_temp_trajectory=[]), SOLVE)
    return len(leads)
print(f"RESULT offgrid_step180min baseline_leads={offgrid(CLS._file_lead_predictions)} mutant_leads={offgrid(MUT)} count")
tail()
