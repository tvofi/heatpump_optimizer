# D2 round 10 -- verifier report (one verifier, lenses V1-V3)

Worktree: detached at handoff/audit-r10-register 9355f107d (the branch was checked out elsewhere, so `--detach`).
Python 3.14.7 seat venv, PYTHONPATH=tests/hastub. All runs under contention: load1 21.9-30.9, thread_factor 1.000. No timing figure is used in any vote.

| id | vote | severity | V1 reproduced | V2 independent | reach | class |
|---|---|---|---|---|---|---|
| D2-s2-01 | weaken | medium | 1.4346 (perturb -> 1.0000; boost 1.2000 -> 1.0000; LOO drop_max 0.4346, 41 cells) | own points: (7,65) 2.660/1.854 = 1.435; (7,50) 1.289; (-10,50) 1.119; (-20,55) 1.000 (both floored) | yes: dhw_planner.py x6, coordinator 3526/4555/9813 | P2 |
| D2-s3-01 | verify | low | 0 of 24, 1.000 kW (perturb -> 5.000 kW) | own driver, 5-min samples, 3 months, peaks_averaged=1: max billed while month==M = 1.0 kW in 3 of 3 | yes: tariff.PeakTracker.observe, read by _roll_month book_capacity | new |
| D2-s3-71 | weaken | low | P1 autumn: fix0.50 -0.1305 ... fix2.00 +0.2458 -> slope 0.251/unit; flat perturbation collapses all arms to +0.0041 | learn arm (aperture learned, #36) -0.0241, none -0.0880: bias exists only on a fixed wrong aperture | yes, but only where the aperture is fixed | new |
| D2-s3-72 | weaken | medium | fix1.00 vent share 0.172 at delivery 0.4, 0.000 at 1.0 | delivery 0.7: 0.000 trips (ua_bias +0.133); fix2.00 at delivery 1.0 trips 0.191 | yes: _learning_frozen returns "ventilation" (coordinator 6350); heat-loss learner returns at 5073 | P5 |
| D2-s1-71 | verify | medium | space_demand_rel_diff 0.4367 (perturb --ratio 1.0 -> 0.0000) | closed form L(r-1)/(U+L) = 141.0*0.922/297.7 = 0.4367 | yes: coordinator 4427 -> 4460 external-heat observation | P2 |
| D2-s3-73 | verify | medium | sysid_adopt_effective_rel_err_A 0.4367 (614.6 vs 427.8 W/K); B 0.0000; perturb -> 0 | same closed form; code: sysid.py:159 and :1233 both raw | yes: coordinator 10981 adoption_decision | P2 |

## Notes per finding

- **D2-s2-01**: the inconsistency is real and the identity fails. Weakened: a given install has one `cop_flow_carnot` value, so no single run prices one tank two ways; the consequence is the direct-branch law's magnitude. The >1 "boost" below 35 C (factor 1 - 0.008*(T-35) = 1.2 at 10 C) points in the physically right direction, since a colder sink raises COP, so that half is not a defect.
- **D2-s3-01**: confirmed by code: the month-change branch zeroes `_window_*` before `_close_window` can run. The consequence is one window in about 720 per month, and it matters only when that window holds the month's peak.
- **D2-s3-71**: the null and the perturbation both behave as stated. The shipped learned-aperture arm carries no material bias (-0.024, noise-sized), so the claim holds for a fixed or mis-set aperture only.
- **D2-s3-72**: the harness patches `_learning_frozen` to None for every arm, so it measures trip share under learners that never freeze. The "freezes every learner" half is established by code reading (coordinator 5000-5073, 6350), not by the harness. Trips need about 60 % delivery bias, or a 2x aperture error: there are 0 trips at delivery 0.7. The trip share under the real freeze (which also blocks the corrective learner) is unmeasured; the starvation release is at coordinator 9367.
- **D2-s1-71 / D2-s3-73**: one cause, raw `lower_floor_heat_loss` in place of `lower_floor_heat_loss_learned`. Seam enumeration (grep `upper_floor_heat_loss +`): raw at coordinator 4427, sysid 159, and sysid 1233; ratio-aware at coordinator 2451, optimizer 1898, and optimizer 4856. Together the two findings cover every raw seam. Each finding alone names only its own seam. The 43.7 % is the owner-shaped state (r = 1.922). It scales as L(r-1)/(U+L) and is 0 at r = 1.
