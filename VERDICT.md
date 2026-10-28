Fix review: blocked ea4630aceaaba32d0e6c79ef16e443de15c4dc66 class-open: _partload_derate accepts every derate in [0, 0.5] whatever the band, and above band/(band+p_max) delivered_heat_kw falls with power
bus-nonce: 3fd38766c2a8d661105749694c7b8194

Reviewer local-reviewer-s10, round 1 of this group's review. Measured at ea4630ace (moved from 05316a9b1 only by github-actions[bot] `ci: pin killed mutants`, three killed_by ledger files). The finder named no harness: dev/audit/harnesses/r10_cop_partload.py is the fixer's own, and I ran it at both ends. The monotonicity probe is mine: ev/monotone_probe.py, the tree's own helpers.

## The block (fix-review.md step 6, a predicate's unguarded domain)

`delivered_heat_kw` = P*(1 - d*(P-Pmin)/band). Its slope at p_max is 1 - d - d*p_max/band, which goes negative once d > band/(band+p_max). `_partload_derate` (`0 <= d <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE`) and the 0-0.5 options selector both accept that domain:

RESULT band [4.0,5.0] d=0.19: d_crit 0.167, peak heat 12.2274 kW at P=4.631 vs 12.1500 kW at p_max NON-MONOTONE
RESULT band [3.0,5.0] d=0.3: d_crit 0.286, peak 10.5125 at P=4.833 vs 10.5000 at p_max NON-MONOTONE
RESULT band [1.0,5.0] d=0.5 (the cap, default band): d_crit 0.444, peak 7.5938 at P=4.5 vs 7.5000 at p_max NON-MONOTONE
RESULT band [1.5,5.0] d=0.19 (the harness's band): monotone

0.19 is the top of the harness's own measured plant range, so the first row is inside physics the PR itself measured. In that domain more electricity buys less heat, which no vapour-compression pump does. Three consequences:
- The buffer charge ceiling reads heat at p_max, so it understates the capacity that a lower power delivers.
- The solver sees the top of the band as dominated.
- The RCA's forward-carried exact inverse ("the positive root ... on the band") no longer has a unique root.
The default 0 is unaffected, so no existing install moves.

Repair: bound the accepted derate below band/(band+p_max). Do it in `_partload_derate`, which needs the two power fields, or clamp it in `partload_factor`. Add a feature check on a narrow band, plus a null at the default band where 0.19 stays accepted. Change the selector or its description to match.

## Everything else checked

RESULT null d=0: delivered_heat_kw bitwise cop*P True, monotone True
RESULT parity d=0.15: scalar vs elementwise bitwise True (n 20000); features' two `_grad_parity` part-load cells ok at head
RESULT null control: 32 of 32 d=0.0 plan lines identical, head vs merge base 0b8f8b585 (r10_cop_partload.py at each tree; base prints `term in tree False`)
RESULT harness at head: grid 27 plants ratio at p_max >= 0.808; spread term vs none min -0.0598 max -0.0094 cheaper 16 dearer 0; flat min -0.0754 max +0.0046 cheaper 10 dearer 4 (body's figures reproduce)
RESULT features.py at head: ALL 4550 FEATURE CHECKS PASSED
RESULT mutation R1 (partload_factor returns 1.0): 7 of 4550 FAILED, the seven part-load checks
RESULT mutation heat_per_cop_kw GUARD_OFF (`if False:`): 6 of 4550 FAILED
RESULT mutation four bypasses in one run (batch twin, extend_dhw_temps, trajectory DHW, optimizer ceiling): 7 of 4550 FAILED; each site has its own check (batch: bitwise + jac parity x2 zones; ceiling; dhw schedule; trajectory)
  all three mutant worktrees restored, 0 dirty files
RESULT env_drift --all: CLAIMED config_flow 2 leaves; NO UNCLAIMED DRIFT 56; NO STALE FIXTURE 56
RESULT claimed_drift.txt == origin/main + config_flow only; claims-for 7.0.5 == VERSION; card file identical; VERSION/manifest/notes untouched
RESULT structure: class_excess_loc 17986 head vs 18038 merge base; STRUCTURE RATCHET PASSED; no budget raise
RESULT CI tests/stress at head: ALL 113 STRESS CHECKS PASSED, including production-call channel and `shoulder: cheaper than holding the setpoint`. At the merge base CI's stress was also ok, so the shoulder red the body attributes to the base is the fixer's arm64 host, not the canonical platform.
RESULT CI mutation at head: MUTATION TABLE PASSED, mutants evaluated (not INCONCLUSIVE); the three added sites are pinned by the bot commit
RESULT class rule: fixer's out-of-tree cop_seams.py (sha1 c628396caf3c) returns 59 sites at head, matching the body; RCA §5 dispositions them. The instrument still lives outside the tree.
Red checks at ea4630ace: none; every gate check is green or skipped.
