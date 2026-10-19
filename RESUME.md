# R10-SETPOINT-BOOST handoff note

Code head a3aee59452bb8ea15807fb405e41f565def4b32d on handoff/r10-setpoint-boost, base 4a3cbcf62e6f5e7b6594d376d714388caf2915cf.

Orchestrator items (not Carry lines in the body):
- Owner note: configured p_max at its true value (tvofi is adjusting the config).
- Pointer: the ceiling probe is R10-CEILING-PROBE (sysid.py cheap-night experiment, later wave); it reads DrawRange.commands.

Proposed new groups (from the demand analysis in the seat report):
- UA-learner bias: the learned loss on a set-point-driven install books several times the metered space delivery; needs a replay root cause.
- Manual-valve buffer not used as a store: a 750 L manual-valve buffer publishes plans identical to no buffer in the synthetic census.
- COP part-load / burst seam: the COP model is power-independent; any part-load or burst term is a model change with its own nulls.

Predicted red: `mutation` (55 added sites, pinned by mutation-autofix after the push).
