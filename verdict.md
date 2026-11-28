Fix review: blocked 375a0057b65a828edfaf7ffa7484d137bcae28e4 test-gap: dhw_planner.py's hand-off of dhw_charge_under_way to commit_charges is unpinned; dropping it ships a step-0 hot-water charge the pump would not start, and block_duty, the group's features block and the full features.py all pass

bus-nonce: 0bf2753a787d0b6b1c8c43292b96541a

## Scope

Later round over the reviewed head 8ec4351288a069c784e7cfa6996b8e1c56c417f6 (fix-review.md step 12). `review_carry.py 8ec4351288 375a0057b65a828edfaf7ffa7484d137bcae28e4` and `review_carry.py 0a0dba2c18 375a0057b65a828edfaf7ffa7484d137bcae28e4` both print `FRESH-REVIEW` (`375a0057b65a828edfaf7ffa7484d137bcae28e4 is not the automatic merge of its parents`). The review is the delta's own production change, read as the PR's own diff at each head (`git diff <merge-base> <head>` at 8ec4351288 against `8f22a3b284`, and at the head against `cb2026c3b5`). That change is two merge resolutions:
- `55abebe95c`/`04cac452c5`: #3863's `charge_running` is threaded through `dhw_charges.commit_charges` and `charge_refusal`. The start-condition symbols are imported from `dhw_start`, and `dhw_planner.py:1200-1210` passes `initial_state.dhw_charge_under_way` to `place_startable` and to `commit_charges`.
- `375a0057b6`: in `optimizer.py` `_combi_flux_exchange.net_under`, main's `start_hour` -> `step_hours=h.step_hours` rename is applied to this branch's moved call. Read at the head: the call matches main's other `simulate_trajectory` call sites. No defect.
`optimizer.py` and `runs.py` are unchanged in the PR's own diff between the two heads.

## Block

- The defect is at `custom_components/heatpump_optimizer/dhw_planner.py:1210`, in `commit_charges(self, schedule, tank, (requirement, max_temp), forced_off, start_below, space_demand, running)`. Its last argument is the merge resolution's own hand-off of `ThermalState.dhw_charge_under_way`. No check pins it. Test 2d pins `commit_charges`' internal forwarding only, because it calls `commit_charges` directly.
- Mutant P1 drops `running`, so the default `True` applies. Mutant P1b passes `True`. Both SURVIVED `tests/block_duty.py` (`ev/block_duty_mut.log`; `ALL 161 BLOCK DUTY CHECKS PASSED` unmutated). Both also SURVIVED the group's features block, `R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges committed on the planner's own store` (`ev/features_mut_part1.log`, NULL SURVIVED; `ev/block_head.log` `ALL 55 FEATURES BLOCK PASSED` at the head). P1 also passes the full `tests/features.py` in a `git archive` copy: `1 of 6346 FEATURE CHECKS FAILED`, and the one failure is `the path that proceeds still stamps a resolvable recorded_at (#363)` `[recorded_at = 'unknown']`, which mutant_run.py documents as failing in any copy (`ev/p1_features_full_tail.txt`). P1 also leaves the finder's harness arms `fixtures` and `hysteresis` byte-identical, because they never pair a running compressor with no charge under way.
- The mutant changes behaviour. The probe is `ev/p1_probe.py`, run from each tree root. It takes golden.capture's fixtures `cycling_cost` and `everything_on` and sets `compressor_running=True`, `dhw_charge_under_way=False`, start hysteresis 1, 3 or 5 K, and tank 40-52 degC. At the head, `everything_on` with k=3 K and t0=52 ships step 0 at 0.000 kW. Under P1 it ships 2.416 kW. With k=5 K, t0=50 gives 0.000 -> 3.877 kW and t0=52 gives 0.000 -> 2.416 kW (`ev/probe_diff.txt`, `ev/probe_head.log`, `ev/probe_p1.log`). Mechanism: with `ChargeRuns.running` the store program starts in a run state, so the kernel places step 0 as a continuation without asking `may_start`. Only `charge_refusal(..., charge_running)` refuses it. A revert of this one argument would bring back #3863's step-0 defect on the commit path, and CI would not catch it: mutation_table's operators include no argument drop.
- To settle it: add a planner-level check in the group's block that drives an engaged solve with a start priced, the compressor running, no charge under way and the tank at or above its start temperature. The check should require step 0 to be off, and the same solve under way should keep the charge as its null. Show P1 failing it.

## Findings

- `tools/audit/seat/review_packet.py render --pr 3805 --head 375a0057b65a828edfaf7ffa7484d137bcae28e4 --reviewed-head 8ec4351288a069c784e7cfa6996b8e1c56c417f6` exited 3 and wrote no packet: `UNAVAILABLE: git merge-base --is-ancestor b2ce461c origin/handoff/audit-r11-roster: fatal: Not a valid object name b2ce461c`. `b2ce461c` is a body-item id in `dev/programme/rosters/wave-r11-groups.json` (`items b2ce461c`), not a commit, and the packet reads it as a SHA. The review scope was derived by hand (`## Scope`). Carry: dismissed: an instrument defect outside this PR's diff, reported here for the dispatcher who rendered the brief; the review it blocked was done by hand

## Evidence

- RESULT head-reviewed=375a0057b65a828edfaf7ffa7484d137bcae28e4 (`ev/HEAD.txt`)
- RESULT merge-tree: `git merge-tree --write-tree origin/main 375a0057b65a828edfaf7ffa7484d137bcae28e4` exit 0 (origin/main `cb2026c3b5`, the head's own parent); no conflict.
- RESULT mutation proof of the body's named mutants, via `mutant_run.py --spec ev/spec_nc.json --cmd 'bash ev/block.sh'` (copy-tree): NULL SURVIVED. NC1_refusal_call, NC2_mask and NC3_drop_unstartable were each KILLED (`ev/features_mut_nc.log`). The body's NC1-NC3 claim holds at this head.
- RESULT finder's harness `dev/audit/harnesses/r11_honest_dhw_runs.py` at the head (Linux, venv-ci, OPENBLAS_CORETYPE=Haswell):
  - `fixtures`: `cycling_cost committed: charges 3, hot-water steps under the floor 0 ..., worst gap 0.439 K` and `everything_on committed: charges 3, ... worst gap 0.438 K`. Both match the body.
  - `hysteresis`: 28 builds, rounds 1 (20) / 2 (8), 8 `start@` refusals, and `drop_unstartable removes from it 0` on all 28. These match the body (`ev/arm_*.log`).
- RESULT `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all origin/main`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE`, rc 0. `cycling_cost` and `everything_on` are CLAIMED (`ev/env_drift.log`).
- RESULT `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`, `module_excess_loc=21649` and `methods_over_200=6`. At origin/main `cb2026c3b5` it reads 21600 and 7. That is the body's +49 raise over main and `methods_over_200` 7 -> 6, re-derived.
- RESULT VERSION, manifest.json and the RELEASE_NOTES.md heading are untouched in the three-dot diff.
- CI: `merge_train.py classify 375a0057b65a828edfaf7ffa7484d137bcae28e4 --pr 3805` printed `WAIT 375a0057b65a828edfaf7ffa7484d137bcae28e4 pending: gate red: none` (rc 3) on every poll from 10:04 to 10:47 UTC (`ev/classify_poll.log`). No red, so no `## Red checks` answer is owed. The block does not rest on CI.
- The container restarted partway through the review and stopped the mutant and CI-poll runs. Each was re-run, and the logs in ev/ are from the re-runs.
