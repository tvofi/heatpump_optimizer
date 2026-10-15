# D7 verify-2 (unit D7#2, finder seat s2/arch-s2)

Worktree: detached at handoff/audit-r10-register 9355f107d (the branch was checked out in r10-repo, so `git worktree add --detach`). python3 3.14.7, PYTHONPATH=tests/hastub. load1 5.2-12.9 (other seats running); every number here is a count, not a timing, so contention does not touch it. thread_factor printed 0.19-1.0.

| id | V1 reproduced | perturbation | V2 independent | vote |
|---|---|---|---|---|
| D7-s2-01 | freq_map_defrost_folds=8 (clean 8); COP gate refuses ('defrosting') | --perturb: 8 -> 0 | source: `_freq_fold_blocked` checks distorted draw, FREEZE_COOLING and `_learning_frozen(CONF_POWER_ENTITY)` only; it never reads defrosting | verify, medium |
| D7-s2-51 | escapes=0 at baseline | patch 01: 0 -> 17 | own mixin class(Mix, HeatPumpOptimizerEntity): resolved native_value not `_finite_scrubbed` = 1 | weaken, low (latent: no mixin in tree today) |
| D7-s2-52 | delta_S +2.6888, copies 68->55, admissible | perturbed delta_S 0 | 23 `round(v` sites in sensor.py | verify, low |
| D7-s2-53 | delta_S +0.9689, 68->63 | perturbed 0 | n/a (shares harness) | verify, low |
| D7-s2-54 | delta_S +0.3789, 68->66 | perturbed 0 | - | verify, low |
| D7-s2-55 | delta_S +0.1880, 68->67 | perturbed 0 | inspect: the two functions' 3 non-doc statements are identical (key, current arg order differs) | verify, low |
| D7-s2-56 | delta_S +1.1717, 68->62 | perturbed 0 | drift claim not independently driven | weaken, low (drift is asserted, not shown to change user-visible output) |
| D7-s2-57 | disagreeing_hours=2 (23.999, 24.0) | - | table: dhw label 24:00, quiet_windows._fmt 00:00 | verify, low |
| D7-s2-58 | implementations=9, disagreeing_inputs=10 | - | own: pump_arbiter._finite_or_none(nan)=nan, (inf)=inf; thermal_model._optional_float(10**400) raises OverflowError | verify, low |
| D7-s2-59 | tokens=522 mismatches=0 | --break: 487 | own: parse_month_range('nov-feb')={1,2,11,12}, parse_day_range('sat-mon')={0,5,6} -- same wrap rule | verify, low |
| D7-s2-60 | implementations 35 (driven 26 in 5 families), disagreeing_probes=3 (0, True, '21.5'); 18 x TypeError on '21.5' | - | rows read back as stated | verify, low (P6 class doubtful: P2) |
| D7-s2-61 | disagreeing_states=3; quiet_windows returns inf for 1e400kW | - | own call: _power_entity_kw(state '1e400', kW) = inf; 'nan' -> None; '-0.4' -> None | verify, low |

Reach (V3): s2-01 reachable in real HA whenever freq_control_mode=control with a compressor-frequency entity and a defrosting pump signal; no stub divergence involved (the gate is pure coordinator logic). s2-51 unreachable today (no mixin). s2-61 needs a power sensor reporting an overflowing float -- reachable but unrealistic. The refactor findings (52-57, 59) are maintainability, not defects.

Class: s2-01 is P2 (one fact -- "this interval is learnable" -- decided by divergent predicates), not new. s2-51 new is acceptable (latent guard-by-__dict__). s2-58 and s2-61 are P2 rather than P3 (no capacity floor/divisor involved; divergent guards at siblings). s2-60 P2 rather than P6 (producer writes the key; the guards diverge).

Seam rules: s2-01 enumerates only the freq_map seam against the learner table (8 learners driven) -- enumerates the phenomenon's learner seams. shape_* AST walks enumerate the shape (seam rule, not hand lists). s2-51's rule walks all 91 concrete classes -- enumerates.
