# R10-SETPOINT-BOOST handoff note

Code head f7e98dbe17c1b6370c5783008aac9f1a502024e4 on handoff/r10-setpoint-boost, base 4a3cbcf62e6f5e7b6594d376d714388caf2915cf.

Orchestrator items (not Carry lines in the body):
- Owner note: configured p_max at its true value (tvofi is adjusting the config).
- Pointer: the ceiling probe is R10-CEILING-PROBE (sysid.py cheap-night experiment, later wave); it reads DrawRange.commands.

Proposed new groups (from the demand analysis in the seat report):
- UA-learner bias: the learned loss on a set-point-driven install books several times the metered space delivery; needs a replay root cause.
- Manual-valve buffer not used as a store: a 750 L manual-valve buffer publishes plans identical to no buffer in the synthetic census.
- COP part-load / burst seam: the COP model is power-independent; any part-load or burst term is a model change with its own nulls.

Predicted red: `mutation`; arch-score repaired (coord_footprint 2498 at base and head) (56 added lines, 59 sites, pinned by mutation-autofix after the push).

Round 1 (verdict v-261901a6, carry-missing) answered with a body-only change; the code head is unchanged.
- Carries: R10-CEILING-PROBE (real maximum; idle absorbing compressor draw), R10-DEMAND-OVERBOOK (over-booking, booked-vs-delivered heat); the set-point-to-draw mapping limitation goes to R10-CEILING-PROBE (coordinator decision), R10-BUFFER-STORE, R10-COP-PARTLOAD.
- pr-contract stays BAD-DEST until the roster PR lands these groups on main.
- Reviewer's R16 survivor pinned at f7e98dbe1 (coordinator decision): the fractional-inlet check through _flow_target; M15 is red, M0-M14 are unchanged.
