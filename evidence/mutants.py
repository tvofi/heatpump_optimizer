import sys
O="custom_components/heatpump_optimizer/optimizer.py"; S="custom_components/heatpump_optimizer/slot_drivers.py"; R="custom_components/heatpump_optimizer/rooms.py"
MUTANTS = {
 "A1_next_temp_to_same": (O, "room_temps[min(i + 1, last)] > temp_min_bounds[i]", "room_temps[i] > temp_min_bounds[i]"),
 "A2_tol_zero": (O, "- room_lifts[i] + 0.15 else reason", "- room_lifts[i] + 0.0 else reason"),
 "A3_any_reason": (O, "REASON_ROOM_FLOOR if reason == REASON_COMFORT_FLOOR\n", "REASON_ROOM_FLOOR if True\n"),
 "A4_lift_unclipped_at0": (O, "lifts = np.maximum(temp_min_bounds - unlifted, 0.0)", "lifts = temp_min_bounds - unlifted"),
 "A5_unlifted_no_mold": (O, "margins - _padded_nonneg(room_lifts, n_steps),\n                                     min_temp_floors, n_steps)", "margins - _padded_nonneg(room_lifts, n_steps),\n                                     None, n_steps)"),
 "A6_lifts_is_input": (O, "lifts = np.maximum(temp_min_bounds - unlifted, 0.0)", "lifts = _padded_nonneg(room_lifts, n_steps)"),
 "A7_ceiling_const": (O, "return np.minimum(low, high - 0.5), comfort, mold", "return np.minimum(low, high - 0.4), comfort, mold"),
 "A8_early_return_drop": (O, "    if margins is None and floors is None:\n        return low, comfort, mold\n", ""),
 "A9_codes_order": (S, '("price_rank", "comfort_floor", "room_lift", "mold_guard", "away", "forecast")', '("price_rank", "comfort_floor", "mold_guard", "away", "forecast", "room_lift")'),
 "A10_comfort_vs_lifted": (S, "(floor - (0.0 if lifts is None else lifts) + half - room)", "(floor + half - room)"),
 "A11_rl_lift_whole_margin": (R, '"room_lifts": lift}', '"room_lifts": margins + lift}'),
 "A12_rl_zero_lift": (R, '"room_lifts": lift}', '"room_lifts": lift * 0.0}'),
 "A13_rl_anylift_guard": (R, "    if not lift.any():\n        return", "    if False:\n        return"),
 "A14_horizon_field_none": (O, "room_lifts=floors[2],", "room_lifts=None,"),
 "A15_limits_not_passed": (O, "step_datetimes, limits.room_lifts,", "step_datetimes, None,"),
 "A16_classify_no_mark": (O, "), room, h.temp_min_bounds, h.room_lifts),", "), room, h.temp_min_bounds, None),"),
 "A17_mold_fill_neg": (O, "mold = np.full(n_steps, -np.inf)", "mold = np.full(n_steps, 0.0)"),
 "A18_rl_push_half": (S, '"room_lift": None if lifts is None else np.clip(lifts / half, 0.0, 1.0)', '"room_lift": None if lifts is None else np.clip(lifts / (2 * half), 0.0, 1.0)'),
}
name = sys.argv[1]
if name == "--list":
    print("\n".join(MUTANTS)); sys.exit(0)
path, old, new = MUTANTS[name]
src = open(path).read()
assert src.count(old) == 1, (name, src.count(old))
open(path, "w").write(src.replace(old, new))
