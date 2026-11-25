"""Reviewer mutants for PR #3838 at d7029ade (string replacements, one site each)."""
import sys
OP = "custom_components/heatpump_optimizer/optimizer.py"
CF = "custom_components/heatpump_optimizer/comfort_floor.py"
M = {
    "K1_margin_add": [(CF, "low = comfort = low + margins", "low = comfort = low")],
    "K2_ceiling": [(CF, "return np.minimum(low, high - 0.5), comfort, mold", "return low, comfort, mold")],
    "K3_mold": [(CF, "low = np.maximum(low, mold)", "low = low")],
    "K4_tol": [(CF, "- room_lifts[i] + 0.15 else reason", "- room_lifts[i] + 0.5 else reason")],
    "K5_nolift": [(CF, "> temp_min_bounds[i] - room_lifts[i] + 0.15", "> temp_min_bounds[i] + 0.15")],
    "K6_nextidx_unguarded": [(CF, "room_temps[min(i + 1, last)]", "room_temps[i + 1]")],
    "K7_sameidx": [(CF, "room_temps[min(i + 1, last)]", "room_temps[i]")],
    "K8_moldpad_truncate": [(CF, "f = np.asarray(floors, dtype=float)[:n_steps]", "f = np.asarray(floors, dtype=float)")],
    "O1_nopad": [(OP, "margins = None if min_temp_margins is None else _padded_nonneg(min_temp_margins, n_steps)",
                  "margins = None if min_temp_margins is None else np.asarray(min_temp_margins, dtype=float)")],
    "O2_nounlift": [(OP, "(0.0 if margins is None else margins) - _padded_nonneg(room_lifts, n_steps), n_steps)",
                     "(0.0 if margins is None else margins), n_steps)")],
    "O3_noclip_E": [(OP, "raised_floor(low, temp_max_bounds, _padded_nonneg(\n                (0.0 if margins is None else margins) - _padded_nonneg(room_lifts, n_steps), n_steps),",
                     "raised_floor(low, temp_max_bounds, (\n                (0.0 if margins is None else margins) - _padded_nonneg(room_lifts, n_steps)),")],
    "O4_liftnotcut": [(OP, "margins) - _padded_nonneg(room_lifts, n_steps), n_steps)", "margins) - np.asarray(room_lifts, dtype=float), n_steps)")],
    "O5_markoff": [(OP, "), room, h.temp_min_bounds, h.room_lifts),", "), room, h.temp_min_bounds, None),")],
    "O6_buildoff": [(OP, "step_datetimes, limits.room_lifts,", "step_datetimes, None,")],
}
if sys.argv[1] == "--list":
    print(" ".join(M)); sys.exit(0)
for path, old, new in M[sys.argv[1]]:
    s = open(path).read()
    if s.count(old) != 1:
        print(f"{sys.argv[1]}: {path} count={s.count(old)}", file=sys.stderr); sys.exit(1)
    open(path, "w").write(s.replace(old, new))
