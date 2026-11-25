# Box D3-g29 working notes (partial, checkpointed)
Probes executed (probe-tree, baseline worktree); every null_delta is 0. Planned classes, pending each key's gate verdict (KILLED overrides):
- candidate: e196155b (solver_status label on a real scipy success above its start), 8171db17 / 2aff1f5c / 000221f3 (exact-tie reasons), 0ea7620c (SHAPE_ALPHA), 213a122a (SHAPE_CONFIDENCE_DAYS)
- equivalent-candidate: 9d455ff4 / 55022279 / 6a75a1ff (COP floored at 1.0 by _cop_law), 13315839 / 2d4e3ff8 (no caller passes threshold; draws never equal it), 4434c1fc (identical for in-contract inputs), 69e4aa41 (trajectory has n+1 states), 8ef84170 / b5d57e4a (buffer cap >= 35 C > 20 C ambient), f062e0cc (differs below 1e-304 only; lead: comment wording)
Reach sweep: probes/reach_sweep.out (50 golden scenarios).
- e196155b KILLED by tests/stress.py (count-based, not timing): 'production calls grew past what work counts vouch' summer/1z/space 87905 vs 81453 = 1.079x > 1.05x (thermal_model.py +6202). Matches the probe's objective_evals 0->2 per success. Non-finding.
- re-fire 2026-11-25 (successor seat): restored checkpoint 49b66a44 (6/16 gated); re-executed all 16 probes in a fresh baseline probe-tree: every RESULT line identical to the checkpointed probes/<key>/probe_<key>.out except load1. Resumed gate_wave.sh run at 2d4e3ff8 (its prior gate was interrupted by the stall, no record).
