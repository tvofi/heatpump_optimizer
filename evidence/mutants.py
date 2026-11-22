"""Reviewer mutants for PR #3838 at 9516fcc5 (string replacements, one site each)."""
import sys

CO = "custom_components/heatpump_optimizer/coordinator.py"
OP = "custom_components/heatpump_optimizer/optimizer.py"
RO = "custom_components/heatpump_optimizer/rooms.py"

SCHED_OLD = "config, state.room_temperature, solve_now)), self._confidence_margins(n), config, solve_now, n),"
SCHED_NEW = 'config, state.room_temperature, solve_now)), self._confidence_margins(n), config, solve_now, n)["min_temp_margins"],'
SCHED_HEAD_OLD = "**rooms.floor_limits(rooms.hold(self, rooms.resolve("
SCHED_HEAD_NEW = "min_temp_margins=rooms.floor_limits(rooms.hold(self, rooms.resolve("
WI_OLD = "**rooms.floor_limits(rooms.lift_of(self), self._confidence_margins(len(horizon.prices)), scratch_config, solve_at, len(horizon.prices)),"
WI_NEW = 'min_temp_margins=rooms.floor_limits(rooms.lift_of(self), self._confidence_margins(len(horizon.prices)), scratch_config, solve_at, len(horizon.prices))["min_temp_margins"],'

M = {
    # prior round's surviving mutant and its halves
    "C1a": [(CO, SCHED_HEAD_OLD, SCHED_HEAD_NEW), (CO, SCHED_OLD, SCHED_NEW)],
    "C1b": [(CO, WI_OLD, WI_NEW)],
    "C1": [(CO, SCHED_HEAD_OLD, SCHED_HEAD_NEW), (CO, SCHED_OLD, SCHED_NEW), (CO, WI_OLD, WI_NEW)],
    # the moved helpers in rooms.py
    "R1_margin_add": [(RO, "low = comfort = low + margins", "low = comfort = low")],
    "R2_ceiling": [(RO, "return np.minimum(low, high - 0.5), comfort, mold", "return low, comfort, mold")],
    "R3_tol": [(RO, "- room_lifts[i] + 0.15 else reason", "- room_lifts[i] + 0.5 else reason")],
    "R4_nolift": [(RO, "> temp_min_bounds[i] - room_lifts[i] + 0.15", "> temp_min_bounds[i] + 0.15")],
    "R7_mold": [(RO, "low = np.maximum(low, mold)", "low = low")],
    # the call site's new padding and unlifted arithmetic
    "R5_nopad": [(OP, "margins = None if min_temp_margins is None else _padded_nonneg(min_temp_margins, n_steps)",
                  "margins = None if min_temp_margins is None else np.asarray(min_temp_margins, dtype=float)")],
    "R6_nounlift": [(OP, "(0.0 if margins is None else margins)\n                                    - _padded_nonneg(room_lifts, n_steps)",
                     "(0.0 if margins is None else margins)")],
    # equivalence probe: restore the pre-move clip of (margins - lifts) at zero
    "E1_oldclip": [(OP, "(0.0 if margins is None else margins)\n                                    - _padded_nonneg(room_lifts, n_steps)",
                    "np.clip((0.0 if margins is None else margins)\n                                    - _padded_nonneg(room_lifts, n_steps), 0.0, None)")],
}

if sys.argv[1] == "--list":
    print(" ".join(M))
    sys.exit(0)
for path, old, new in M[sys.argv[1]]:
    s = open(path).read()
    if s.count(old) != 1:
        print(f"{sys.argv[1]}: {path} count={s.count(old)}", file=sys.stderr)
        sys.exit(1)
    open(path, "w").write(s.replace(old, new))
