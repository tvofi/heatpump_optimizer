Fix review: blocked d710a5af5bb2dd1263a5b72b77cdf8ecc011390b claim-drift: on the CI runner (tests / fast (3.14), job 121296829654) env_drift.py --all fails: the claimed away_setback and valve_storage_small_tank are STALE and valve_storage_flat_prices (4 leaves) and valve_storage_low_target (3 leaves) move unclaimed

bus-nonce: 3ce70f9641fb1cef85c0592f42614eba

## Block

This is fix-review round 3 of #2819 (R10-ARCH-SHAPES), from the cloud reviewer seat, claim `rev-2819-3ce70f96`.

- **Head.** `d710a5af5bb2dd1263a5b72b77cdf8ecc011390b`, measured from detached worktrees. `git ls-remote` showed it was still `refs/pull/2819/head` when this verdict was written.
- **Merge base.** `f3ffb1c635327365841ad430ce8fad7488a02d61`, which is origin/main.
- **Delta.** `734ad21fa..d710a5af5`: the fixer's commits `63c71616c` and `b2a55c4a9`, plus main merges.
- **Roles.** `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.

**claim-drift (step 4; orchestrator ruling 3 makes CI `tests / fast` the judge).** `tests / fast (3.14)` concluded `failure` on this head. Its only failed script is `python3 tests/env_drift.py --all f3ffb1c63...` (`ev/ci_fast_script_lines_d710a5af.txt`, `ev/ci_fast_env_drift_d710a5af.txt`). On the runner:

- `STALE claim for away_setback: nothing drifted, remove it`
- `STALE claim for valve_storage_small_tank: nothing drifted, remove it`
- `DRIFT valve_storage_flat_prices: 4 leaves`, `space_reasons[28..31]` `cheap_price -> idle_coasting`
- `DRIFT valve_storage_low_target: 3 leaves`:
  - `space_reasons[87]` `comfort_floor -> idle`
  - `[88]` `scheduled -> idle_coasting`
  - `[90]` `terminal_value -> idle_coasting`
- `2 UNCLAIMED DRIFT(S)`, plus the `RUNNER-CONDITIONAL CANDIDATE (#996 class)` text for both claims.

The two claims this round added were taken from the round-2 reviewer's reading. They do not reproduce on the runner. Round 2 asked for the drift to be "re-run on Linux with the runner as judge", and this result is that re-run. The body's statements are refuted at this head:

- "CI tests/fast on this head ... is the confirmation";
- the #996 comment's "CI tests/fast on b2a55c4a9 confirms it".

**Why claiming one reading does not converge (the cause, measured).** The drift's direction is the same in every environment: a sub-running share the plan calls off becomes idle. That matches D8-s1-01's classifier change. But the set of scenarios it lands on depends on the numeric environment, and the runner has had two numeric environments today:

| environment | `numeric_probe` | `numpy_build` | non-may-drift scenarios that move |
|---|---|---|---|
| runner at `734ad21fa` (job 121260837344, `ev/ci_fast_env_drift_734ad21f.txt`) | `37fadb5234b8` | `ee41918c4ccd` | `valve_storage_small_tank` only |
| this seat and the round-2 seat (cloud container, `ev/env_drift_all.txt`, rc=0 against these claims) | `37fadb5234b8` | `6411f37f1299` | `away_setback`, `valve_storage_small_tank` |
| runner at this head (job 121296829654) | `cacff2cda4b5` | `442b5ddcb90d` | `valve_storage_flat_prices`, `valve_storage_low_target` |
| macOS arm64 (body) | n/a | n/a | `dhw_cold_tank`, `horizon_48h` |

- **The runner is not one environment.** Its two runs on this PR share `interpreter` and `platform` keys, but `numeric_probe` and `numpy_build` differ.
- **Any fixed claim set can go STALE or UNCLAIMED on the next runner host.** That covers re-claiming the runner's latest pair as well. A third repair round of the same shape can fail the same way.
- **This seat's Linux container is not the runner either.** The round-2 block treated it as the runner, and I reproduce its reading exactly here (`NO UNCLAIMED DRIFT`, `NO STALE FIXTURE`, rc=0). That makes it a third environment, not a confirmation.

**To unblock.** This is the orchestrator's call, not a fixer repair:

- either claim the runner's current pair and accept that the claim may flip on the next host;
- or decide how a classifier change whose leaves are BLAS-host-conditional is recorded on #996, for example by naming the affected fixtures for the run, or by pinning the runner's numeric environment.

Everything else this round touches is sound (Evidence). If the orchestrator rules the claim question separately, this verdict has no other block.

## Findings

- **The judge of record moved under the claim protocol.** The CI runner's `numeric_probe` changed from `37fadb5234b8` to `cacff2cda4b5` between two `tests / fast` runs on this PR on the same day. `env_drift.py`'s #996 decision tree ("the runner is the judge of record") assumes one runner reading. With two, a claim-bearing PR whose drift is BLAS-conditional cannot be made green reliably by any claim set. A cloud reviewer's Linux container is a third reading, so the round-2 advice to claim it was unsound. Carry: #996
- **Unclaimed may-drift movers this diff causes go unrecorded in the body.** On the runner, eight may-drift fixtures moved in exactly this PR's direction (`-> idle_coasting` / `-> idle`): `direct_flow_carnot`, `shoulder_two_zone`, `valve_storage`, `valve_upper_direct_slab`, `winter_two_zone_dhw`, `wood_coil` (12 leaves), `wood_two_tank` and `wood_two_tank_smart_write`. They pass only because each holds a may-drift entry granted for an older, unrelated cause (#1207/#1208). The body names none of them. `env_drift.py` refuses to let a fixture be both claimed and may-drift, so the tool cannot record this PR's movement on them. Carry: R10-ARCH-SHAPES
- **Unpinned sites still owed.** `tests / mutation` refuses 75 sites added by this diff (`ev/ci_mutation.txt`). `ci_predict.py` gives 74 lines, one of them `quiet_windows.py:343 CMP_BOUND*2`, which matches the body's 74-line list exactly. `tests / mutation-autofix` again ended `AUTOFIX: skip-measure-failed -- THE REPAIR DID NOT HAPPEN` (`ev/ci_mutation_autofix.txt`). The pin run, and a killing check or `survivor_triage` entry for any survivor, are still owed before merge, as the body's `## Red checks` says. Carry: R10-ARCH-SHAPES
- **P2 rule reach, residual spellings.** With the round-3 rule, a planted `np.greater(p, 0.05)` (a ufunc call, not a Compare) and a local-bound line (`line = 0.05; p > line`) are not returned (`ev/p2_rule_null_controls.txt`). A grep of every `0.05` in `custom_components/heatpump_optimizer/*.py` finds no production instance of either spelling, so this is an instrument gap and not an open seam. Carry: R10-ARCH-SHAPES
- **Body text.**
  - `## Head` carries a second paragraph naming `ac87aaf9e021c148d2bfabdccc29ed3ee5e73215`, which is not an object in the repository (`git cat-file` fails).
  - The Figures line "71 unpinned sites, listed below" is the round-2 count, beside the round-3 count of 74.
  - The `tests / fast` red-check answer says no seat can run `env_drift.py --all` on Linux. A cloud seat can, but per the first finding its reading is not the runner's either.

  Carry: R10-ARCH-SHAPES

## Evidence

- **Round-2 block, item 1 (claim-drift):** not fixed on the runner (Block). On this seat's container the round-2 reading reproduces exactly: `ev/env_drift_all.txt`, `CLAIMED away_setback: 4 leaves`, `CLAIMED valve_storage_small_tank: 1 leaves`, `dhw_cold_tank` / `horizon_48h` byte-identical, `NO UNCLAIMED DRIFT`, `NO STALE FIXTURE`, rc=0.
- **Round-2 block, item 2 (class-open on `step_duty` / `dhw_heating_active`):** settled by orchestrator ruling 2. The body now dispositions both seats under "Seats that test a circuit against the pump's running floor", with the owner named (D12-s2-01, #1955). Not re-litigated.
- **Round-2 findings, re-checked at this head.**
  - Instrument reach: the round-3 rule (`tests/entities.py::_p2_match_channel_line`) now returns the chained, `line=`, keyword-only, `override` and `5e-2` spellings and a lambda default (`ev/p2_rule_null_controls.txt`, planted into a `topology.py` copy).
  - `coordinator.py::_run_system_identification` now reads `planned_draw_runs(float(override))`. This is the third coordinator hunk, in scope by ruling 1. `git diff 734ad21fa d710a5af5 -- custom_components/heatpump_optimizer/coordinator.py` is that one line.
  - `accuracy.py::AccuracyTracker.power_ratio` is dispositioned.
  - `AccuracySample.from_dict.num` now reads `const.finite_float`.
  - The "Architect note amendment" now calls the hunks running-rule plumbing.
- **Mutation proof, round-3 hunks** (`ev/mutants.txt`, `ev/feat_m*.txt`), `git archive` copies of the head, `PYTHONPATH=tests/hastub python3 tests/features.py`:
  - control `1 of 4411 FEATURE CHECKS FAILED`, the archive-only #363 `recorded_at` check;
  - `heat_pump_on` back to `override > 0.05`: `2 of 4411`, the extra FAIL is "an experiment command under the running floor does not mark the pump on (D8-s1-01)" `[2.0 kW -> True, 0.07 kW -> True]`;
  - `num` back to the base's bare `float()`: `2 of 4411`, the extra FAIL is "a stored sample's numbers go through const.finite_float ..." `[True used to load as 1.0]`.

  Both are killed. I did not re-run the rule mutant in `tests/entities.py`. CI's `tests/entities.py` is `ok` at this head.
- **Finder harness**, `dev/audit/rounds/round10/D8/s1/f1_active_now.py` (sha1 `766cc95a3b886f3f70d122a167028d2313d78048`, identical at both ends), with `PYTHONPATH=tests/hastub:custom_components` on Linux x86_64 (`ev/f1_*.txt`):

  | end | heating_now_while_off | slot_steps_declared_off | --perturb |
  |---|---|---|---|
  | `da12aa37d` (fixer's base) | 2 | 5 | 0 / 5 |
  | `f3ffb1c63` (merge base) | 2 | 5 | 0 / 5 |
  | `734ad21fa` (round 2) | 0 | 0 | 0 / 0 |
  | head | 0 | 0 | 0 / 0 |

  `snapshots=36` and `steps=192` everywhere, and `perturbed=1` on every `--perturb` run.
- **Companion**, `dev/audit/harnesses/r10_channel_running_rule.py` (`ev/companion.txt`):
  - merge base: slot 5, reason 5, sensor 2 (`'2 heating periods'`);
  - head: 0 / 0 / 0 (`sensor_state=None`);
  - `--perturb`: 0 / 0 / 0 at both ends.

  The three counters fall as sets, matching the body.
- **Class enumeration**, `dev/audit/harnesses/r10_channel_line_reach.py <head rule> <tree>` (`ev/reach_*.txt`): `RESULT hits=26` at the merge base and `RESULT hits=19` at the head, which matches the body. Every head site is the owner or a body disposition.
- **Class sweep beyond the literal.** I grepped production comparisons of power, draw or schedule values against literals other than 0.05. `coordinator.py::_detect_immersion` `_commanded_power() > 0.1` is dispositioned in `plan_running_rule`. `optimizer.py` `dhw_heating_active` falls under ruling 2. `coordinator.py::_replay_interval` `dhw_kw > 0.0 or space_kw <= 0.0` is a split-interval test on the commanded split, not the channel-heating question. No new seam was found.
- **Architecture and structure** (`ev/structure_archscore.txt`): `STRUCTURE RATCHET PASSED`. `score.py --diff da12aa37d HEAD` and `--diff f3ffb1c63 HEAD` both give `Architecture score: dS +1.8325 IMPROVES`:
  - duplication_copies 38 -> 35;
  - coord_footprint 2446 -> 2437;
  - params_over_10 7 -> 6;
  - layer_violations 17 -> 13;
  - private_cross_module 12 -> 10.

  This matches the body. Per ruling 2, I did not block on the round-2 +1.
- **Claims file** (`ev/claim_diff.txt`). The three-dot diff against the merge base is the two added lines only. `claims-for: 7.0.4` equals `VERSION` 7.0.4. Each line states its direction. Neither scenario is may-drift.
- **Release stamps.** `VERSION`, the manifest and `RELEASE_NOTES.md` have an empty three-dot diff.
- **Merge.** `git merge-tree --write-tree origin/main d710a5af5` exits rc=0 with tree `48c7263e7` and no conflict (`ev/merge_tree.txt`).
- **#996 instance lines** (ruling 4). Comment 6402685018 exists on #996. Its "CI confirms it" line is refuted by the runner (Block).
- **CI on this head** (check-runs API, `ev/check_runs.txt`, 42 success at write time). Red:
  - `tests / fast (3.14)`: the Block.
  - `tests / mutation`: the predicted unpinned-sites red, answered in the body's `## Red checks`.
  - `tests / mutation-autofix`: skip-measure-failed, answered in the body.
  - `governance / delivery-status`: OVERDUE on #2798, #2799, #2780, #2749, #2775, #2797, #2762 and #2795, not #2819. Its log says "This check is NOT a required context and a red here blocks no merge" (`ev/ci_delivery_status.txt`), so it is not this PR's.

  `pr-contract` was still queued and `prelude` in progress, so step 11's posting condition has not concluded. No root-cause block is raised.
- **Head SHA in the body.** `## Head` names `d710a5af5bb2dd1263a5b72b77cdf8ecc011390b`, the head I measured. I re-read it before writing.
