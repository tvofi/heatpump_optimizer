# D2 verify unit 1 (round 11) — all lenses

All six findings carry planted scopes (D2-s1, D2-s2), so every number below was measured in the private copy of the planted export, `../audit-r11-px-D2-1`, run with PYTHONPATH=tests/hastub (V2 added `.`), using the r10s6 venv-ci python. The finder harnesses are counts, not timings. Measured at load1 between 5.9 and 7.5, thread_factor between 1.0 and 1.006.

| id | V1 baseline -> perturbation | V2 (my own probe, production function) | V3 | vote |
|---|---|---|---|---|
| D2-s1-01 | batch_parity total 14292 (the claim says 14897), 2z valve 11245; `--fix-lift` -> 3012, perturbation_fix_lift=1 | flow_lift_factor(outdoor 0, flow 60) = 1.586; the physical carnot_flow/carnot_ref = 0.631 (45 C: 1.245 vs 0.803) | reachable: scalar compute_cop on every plan; class P2 (one fact decided twice, scalar vs batch); the seam rule names only the lift seam | verify, count corrected to 14292 |
| D2-s2-01 | lift_over1=84350, carnot_frac_over1=21320, batch_parity_maxabs=8.009; `--perturb=lift` -> all 0 | same 1.586 at 60 C; this is a duplicate of D2-s1-01 | reachable; P2 confirmed | verify (dedup with D2-s1-01 for the judge) |
| D2-s1-02 | after `--fix-emitter` the mismatches go 14292 -> 8830 total; the finder's 3674 count is after 01 is fixed; perturbation_fix_emitter=1 | emitter_delivery(mix 18, zone 21, ua 0.3) = -0.90 kW; the docstring says "Never negative" | reachable: thermal_model.py:2526 and :2536 (two-zone valve step); class P2 (the batch twin floors, the scalar does not); 87.52 kWh not re-derived | verify |
| D2-s2-02 | duty_law_mismatch 60, duty_law_at_0.2 = 1.0; `--perturb=defrost` -> 0 and 0.70 (winter_mild, shoulder frost_cop_ratio 1.0 -> 0.70) | derate_from_duty(0.2) = 1.0; defrost.py:205 `1.0 + duty * ...` against its docstring `1 - duty x` | reachable wherever measured defrost duty is learned; class new (sign inversion) | verify |
| D2-s2-03 | clamp_mismatch total 3 -> 0 under `--perturb`; on_off sub_pmin_steps 26 per unit (the claim says 32 of 96); auto clamps with 0 | declared_modulation({on_off}) = True; thermal_model.py:1473 returns True for ON_OFF, and its docstring says False | reachable through the options flow; class new; the seam rule enumerates the declared-modulation seam only | verify, count corrected to 26 |
| D2-s1-51 | cells 36, inverted 36, null control 0; ratio 1.545-1.546; `--perturb` -> 0.637 | presets.py:107-113: low_energy 0.85 > 1980_2005 0.80 > post_2005 0.55; 0.85/0.55 = 1.545 | reachable through the preset derive in config flow; class new | verify |

Severity: 01/s2-01 high (they invert COP pricing on every hot-flow and DHW plan); s1-02 high (negative heat in the valved step); s2-02 medium; s2-03 medium; s1-51 medium.
