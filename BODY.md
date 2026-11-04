R10-ARCH-SHAPES-CLASSIFIER: land the reason-classifier arm of D8-s1-01 that #2819 parked, the folded R10-HOTFIX-PREHEAT-LABEL fix, and the four #2238 sweep-P2 seams routed here, with the classifier drift claimed by shape.

- **Classifier arm (Carry 4).** `classify_space_steps` / `classify_dhw_steps` read each channel's draw through `_heating_draws`, which calls `thermal_model.channel_heating_draw`: the draw on the steps `channel_heating_steps` says the channel heats, 0 elsewhere. A share on a step the plan runs no pump at is now idle to the classifiers, as it already is to the plan views, pump schedule and wood advisor. Starting point: the parked `996b54cf1`. Main had since moved `channel_heating_steps` into `thermal_model.py`, so `channel_heating_draw` moved there beside it. The two `tests/entities.py` dispositions go back to the owner-module reading.
- **Pre-heat label (Carry 8, 9).** The four commits from `handoff-wip/r10-hotfix-preheat-label` (`9bfbe3866`) were cherry-picked unchanged. `_weather_loss_factors` divides each step's loss by the same house's calm, dry loss. The learned `house_heat_loss_scale` therefore no longer reads as weather in `preheat_weather` or in the warm start. At scale 1.0 the output is bit-identical to before.
- **Four P2 seams (Carry 6, 7).** `FrequencyMap.recommend`, `FrequencyMap.evidence_exhausted`, `_async_learn_buffer_cooling`'s `heating` and `_observe_frequency`'s `watch_active` each call `thermal_model.planned_draw_runs` in place of their own 0.05 kW copy.
  - Having `freq_control` read `thermal_model` would close an import cycle (entry_config → freq_control → thermal_model → entry_config). The two `FREQ_MODE_*` strings, which several modules share and `entry_config` parses, therefore move to `const.py`, and `freq_control` re-exports them explicitly.
  - Alternatives that lost: a function-level lazy import hides the cycle instead of removing it. Passing a `runs` flag into `FrequencyMap` would leave the decision with every caller. A new leaf module for the running rule would be a new tracked file outside every measured closure, for a two-constant problem.
- **Stress invariant.** `tests/stress.py`'s "heating steps have no reason code" counted a raw space draw over 0.05 kW as heating, which is a copy of the line this group retires. `winter_extreme/2z/space` puts a share on a step the plan calls off, and the classifier now rightly calls that step idle, so the invariant failed. It now asks `channel_heating_steps`.
- **Claim (Carry 0, 1, 5).** `tests/golden/claimed_drift.txt` restates its header with the SHAPE category and claims `shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'`. There is no fixed fixture list.


**Roster carries.** The review packet numbers carries 1-based, while the brief's "Carry N" labels are the roster's 0-based indexes. Each is named here in the packet's numbering, with the brief's label in brackets:
- Carry 1 [brief 0]: done. The claim-file header now names the SHAPE line, restated with this branch's claim.
- Carry 2 [brief 1]: done. The claim is `shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'`, and `r10_shape_claim_controls.sh` was re-run (`## Figures`).
- Carry 3 [roster 2, from #2843]: the same header carry as Carry 1, done by the same change.
- Carry 4 [roster 3, from #2843]: the same claim carry as Carry 2, done by the same change.
- Carry 5 [brief 4]: done. The parked arm (`996b54cf1`) landed, with `channel_heating_draw` beside `channel_heating_steps` in `thermal_model.py`.
- Carry 6 [brief 5]: done. The claim is by shape, not a fixture list. The census was not re-run (`## Figures` says why).
- Carry 7 [brief 6]: done. The four seams call `planned_draw_runs`, and the precondition and null were re-measured with the rebuilt probe harness.
- Carry 8 [brief 7]: the routing record for Carry 7's four seams. It is discharged by the same change.
- Carry 9 [brief 8]: done. The pre-heat label fix landed, with all three controls and the mutant.
- Carry 10 [brief 9]: done. The four WIP commits were taken from `9bfbe3866`. The scoped gate and `features.py` ran at the head, prepr ran with `## Unpinned sites` (both CLAMP_DROP floors included), and the body is this one.

## Head

825f8ecd0506076463683a766863a23793521386 (code head pushed to `handoff/r10-arch-shapes-classifier`). It is PR head c34999c1dd512e45fea3027bc49da31a78050d8a (the handoff 913e74e87 plus the bot commit `ci: pin killed mutants`) plus two commits of repair round 2, 2026-11-04: the new features check, then the pin json for the one site it kills. Merge base c3a279e3252a8b57bb00b5a677318cd4fe20387f. `origin/main` moved during the repair (a9c2f90f to 8e90d81443317f76f22602a89651f7ca17c633f9, fetched 2026-11-04 after the first `prepr.sh` run predicted `governance / wave-script AGREEMENT UNMERGED` and `GRADER UNMERGED`), so the head is a merge commit (`git merge origin/main`, no conflict; the ledger driver resolved `tests/structure_budgets.json` and `tests/closures.json`). Steps 2-8 were re-executed on the merged tree: `tests/features.py` printed `ALL 4786 FEATURE CHECKS PASSED`, `tests/entities.py` `ALL 2602 ENTITY CHECKS PASSED`, `tests/structure.py` `STRUCTURE RATCHET PASSED`, and `tools/pr/prepr.sh` ended `PRE-PR: <head> rc=0` with `ci predict` reading no predicted red against 8e90d8144331. `tests/golden/claimed_drift.txt` differs from origin/main by the ten lines of this PR's own shape claim (`## Figures`, unchanged since the first handoff); `card_claimed_drift.txt` is identical to origin/main, and VERSION, the manifest version and the `RELEASE_NOTES.md` heading are untouched.

## Mutation proof

One combined mutant, in a worktree at head b03b76d5d, ran `PYTHONPATH=tests/hastub python3 tests/features.py` and reported `7 of 4785 FEATURE CHECKS FAILED`. The reverted lines were:
- the two `_heating_draws` lines;
- `_weather_loss_factors`'s `calm_loss`, set back to the raw nameplate (`calm_loss = base_loss`);
- both `freq_control` gates, back to `target_kw <= 0.05`;
- both coordinator predicates, back to `> 0.05`.

Each failing check exercises a single seam:
- FAIL a target the plan calls off asks the map for nothing (D8-s1-01). Killed by the freq_control gates.
- FAIL a learned heat-loss scale of 1.24 under a flat forecast labels no step weather pre-heating, and the plan does heat. Killed by `calm_loss`.
- FAIL a forecast wind spell still labels weather pre-heating, at scale 1.0 and 1.24, and only on the spell's steps. Killed by `calm_loss`.
- FAIL a step the plan runs no pump at is idle to the reason classifiers (D8-s1-01). Killed by `_heating_draws`.
- FAIL the buffer learner reads heating from the plan's running rule. Killed by `heating`.
- FAIL the watchdog's two bounds: the floor is exclusive, the minimum inclusive. Killed by `watch_active` at `MIN_RUNNING_DRAW_KW`.
- FAIL a step the plan calls off is not watched (D8-s1-01, #2238 sweep P2). Killed by `watch_active`.

With the code restored, the gate's features run read `ALL 4785 FEATURE CHECKS PASSED`.

**Repair round 2: the evidence_exhausted gate in isolation.** The review of 913e74e8 found that "a target the plan calls off asks the map for nothing (D8-s1-01)" does not kill `freq_control.py:228 GUARD_OFF`: its map holds buckets at 2.0 to 6.0 kW, so `evidence_exhausted(0.07)` reads False with or without the gate. The new check "evidence below a target the plan calls off is not exhaustion (D8-s1-01)" builds a map whose one bucket predicts 0.06 kW (`observe(25.0, 0.06, 20.0, 120.0)` repeated `FREQ_MIN_SAMPLES + 1` times) and requires `evidence_exhausted(0.07)` False and, as its null control on the same map, `evidence_exhausted(0.11)` True.
- With the gate replaced by `if False:` (the one mutated line, nothing else), `PYTHONPATH=tests/hastub python3 tests/features.py` printed `FAIL evidence below a target the plan calls off is not exhaustion (D8-s1-01)`, `1 of 4786 FEATURE CHECKS FAILED` and `rc=1`.
- With the file restored by `git checkout`, the same command printed `ALL 4786 FEATURE CHECKS PASSED`.
- `python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3` printed `pinned   custom_components/heatpump_optimizer/freq_control.py:228 GUARD_OFF -- killed by tests/features.py` and `PIN KILLED: 1 pinned, 0 left unpinned`. The null control `freq_control.py:33 NULL_COMMENT` survived every driver, as it must. The pin json is `tests/mutation_ledger/killed_by/freq_control.py/FrequencyMap.evidence_exhausted.GUARD_OFF.39c9b8d5.json`, committed.

The combined run does not show that each check kills its own mutant in isolation. Each check drives only its own seam, but a reviewer wanting per-mutant runs needs to rerun them. The preheat fixer's commit 589f65e2d recorded "Main's code fails exactly the first two" of its tests.

## Null control

- **Probes.** `dev/audit/harnesses/r10_run_owner_probes.py --perturb` at the merge base swaps each 0.05 kW copy (and the classifiers' `CHANNEL_ACTIVE_KW` default) for the owner's value on a temp copy, and reads `probes_failed=0`. Unperturbed, the base reads 6. The 0 at head is therefore the owner's rule and not a probe that cannot fail.
- **Pre-heat.** Scale 1.0 under a flat forecast is unchanged: it is a features check. The finder's arm 4 (configured, no learned scale) reads 0 of 96 at both ends.
- **Claim controls.** `r10_shape_claim_controls.sh` at BASE plus a comment-only production line reads rc=1, with the claim STALE. The narrow claim without `dhw_reasons[*]` reads rc=1, UNCLAIMED.
- **Freq map.** At 0.11 kW, a step the plan runs, the map still recommends.
- **Buffer learner.** At 0.5 kW the learner still reads heating.
- **Watchdog.** At 2.0 kW and 45 Hz, a running plan is still watched.

## Figures

Repair round 2 additions: `python3 tests/entities.py` printed `ALL 2602 ENTITY CHECKS PASSED`; `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED` (`seam_cut_total 423 <= 423`); `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` printed `MODE: SCOPED -- 29 script(s) run, 4 scoped out`. The commands for the first block of figures below are unchanged and were taken as stated there.

All figures below were taken at head 2bf3bed46 unless marked otherwise. The head c4d45522c669 adds only the tests/closures.json INERT entry. Toolchain: `bash tools/audit/seat/cloud-setup.sh` refreshed the venvs, and `cloud-setup.sh --check` printed OK. Afterwards, `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'` printed `2.5.4 1.18.1`, which matches tests/requirements-ci.txt. CI stays the authority for goldens.

**Scoped gate and per-script checks**
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` printed `MODE: SCOPED -- 29 script(s) run, 4 scoped out` at b03b76d5d. That diff later added tests/stress.py, which the scope already ran. At head c4d45522c669 the diff also touches tests/closures.json (the INERT entry), which the gate cannot scope, so prepr skipped its closures step and CI runs the full suite.
- `GATE_SCOPE=auto GOLDEN_MODE=drift ./tests/run.sh` at b03b76d5d went red on three scripts: typing_ruler, stress and harness_headers. All three are answered under `## Red checks` and were fixed in 2bf3bed46 (head c4d45522c669 adds only the closures INERT entry). Every other script in scope passed, including `ALL 4785 FEATURE CHECKS PASSED`, `ALL 2602 ENTITY CHECKS PASSED` and `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` printed `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/typing_ruler.py` with HPO_TYPING_PYTHON=/opt/hpo/venv-ha/bin/python printed `ALL 9 typing-ruler checks PASSED` and `ALL 12 typing-ruler source checks PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/stress.py` printed `ALL 113 STRESS CHECKS PASSED`.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `class_excess_loc` went 17640 → 17633, recorded in e3daad4d2. That commit's message says 17655 → 17648 because it was written at the preheat branch's older base. The row moves by the same -7: `_weather_loss_factors` left `HeatPumpOptimizer.optimize`. No other row moved.

**Goldens and the shape claim**
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all c3a279e32` without the claim (at e8c8de8e2) printed `4 UNCLAIMED DRIFT(S)`. The four were away_setback, valve_storage_flat_prices, valve_storage_low_target and valve_storage_small_tank. Every moved leaf on this host, may-drift fixtures included, was a `space_reasons[i]`/`dhw_reasons[i]` leaf moving to `'idle_coasting'`. Rule: the drift log's leaf lines, read by eye.
- The same command with the claim (at 5fb4f381a) printed `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`, with four `SHAPED` lines.
- `bash dev/audit/harnesses/r10_shape_claim_controls.sh e8c8de8e2 c3a279e32 $OUT` printed `RESULT after_rc=0`, `RESULT narrow_rc=1` and `RESULT null_rc=1`. ARM is the last production commit before the claim, because the harness appends its own claim line.
- The census `dev/audit/harnesses/r10_band_census.py` was not re-run here, because it costs about 25 minutes per host. This host's movers are the env_drift run above, and the claim is by shape, so the census's susceptible set is not an input to it.

**P2 probes (Carry 6 precondition and control)**
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_run_owner_probes.py` printed `RESULT probes_failed=0 count` of 6 at head, `probes_failed=6` at the merge base, and `probes_failed=0` at the merge base with `--perturb`.
- The committed `dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py` at the merge base was run with `defrost_interval` bound in the sixth probe's namespace, on a scratch copy. It printed `RESULT probes_failed=6 count` of 6. The new harness is that probe rebuilt: expressions are found by the local they are assigned to, and the null is rebuilt for this tree.

**Class enumeration (step 8)**
`python3 dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py` printed `RESULT F1_run_threshold=13 count` at the merge base and `=9` at head. The four seams that left are exactly the four fixed here. The remaining nine are dispositioned as follows:
- accuracy `delivered_ratio` ×2: a ratio-denominator floor. Registry disposition `accuracy.py::delivered_ratio`.
- climate `hvac_action`: ORed with `heat_pump_on`. Registry disposition `climate.py::HeatPumpOptimizerClimate.hvac_action`.
- coordinator `_detect_immersion`: registry disposition.
- coordinator `_capacity_caps` and `_fold_capacity_envelope` (`p_max <= 0.1`): a capacity bound on the plant's maximum power, not "the plan runs this step". The P2 matcher does not return them.
- dhw_learning `async_learn_usage`: registry disposition.
- freq_control `observe`: a floor on a METERED draw. Registry disposition `freq_control.py::FrequencyMap.observe`.
- optimizer `get_current_action`: registry disposition.

The registry is `tests/entities.py`'s `_p2_registry`, fact `channel_active_kw`. It refused the four now-stale dispositions until they were removed, which is the check's own null.

**Finder harness, pre-heat label**
The probe is the inline harness in handoff-body/r10-live-plan-energy `7c4e639e4` BODY.md, saved as `probe.py` (sha1 9978dbb2f60eaaaf6da48e591ba739901be94d9b). A companion drives its arms and counts `space_reasons.count('preheat_weather')`. Both live in scratch.

| arm | base c3a279e32 | head |
|---|---|---|
| 1 (as configured) | 88 of 96 | 0 |
| 7b (flat price, flat 6 °C) | 88 | 0 |
| s1 (scale only) | 74 | 0 |
| s3 (outdoor 3 °C) | 88 | 0 |
| 4 (no learned scale, null) | 0 | 0 |

The positive control is the features check that labels a forecast wind spell at both scales.

## Unpinned sites

Seven sites are pinned by `mutation-autofix` (`ci: pin killed mutants`, c34999c1); the eighth, freq_control.py:228, is pinned by this seat's `--pin-killed` run. The check named against each is the one expected to kill it, and that lane's run is the proof.
- `custom_components/heatpump_optimizer/coordinator.py:10621 CMP_BOUND`: killed by "the watchdog's two bounds: the floor is exclusive, the minimum inclusive" (`_p8s_watch(2.0, 20.0) == [True]` at `reported == hz_min`).
- `custom_components/heatpump_optimizer/freq_control.py:201 GUARD_OFF`: killed by "a target the plan calls off asks the map for nothing (D8-s1-01)" (recommend at 0.07 kW answers a frequency).
- `custom_components/heatpump_optimizer/freq_control.py:228 GUARD_OFF`: the earlier claim that "a target the plan calls off asks the map for nothing" kills it was wrong (review of 913e74e8). It is killed by the new check "evidence below a target the plan calls off is not exhaustion (D8-s1-01)" (`## Mutation proof`, repair round 2) and pinned by the committed json; the bot's `ci: pin killed mutants` pinned the other seven.
- `custom_components/heatpump_optimizer/optimizer.py:340 CLAMP_DROP`: killed by "pin _weather_loss_factors' two floors by value" (9bfbe3866): with a zero nameplate, dropping the 0.001 floor gives a flat 0.
- `custom_components/heatpump_optimizer/optimizer.py:341 CLAMP_DROP`: killed by the same floor check: with a zero learned scale, dropping the 1e-9 floor divides 0 by 0 (NaN).
- `custom_components/heatpump_optimizer/optimizer.py:1421 GUARD_OFF`: killed by every classifier call with `other=None`, which then reaches `channel_heating_draw(None, ...)` ("a step the plan runs no pump at is idle to the reason classifiers (D8-s1-01)" among them).
- `custom_components/heatpump_optimizer/optimizer.py:1423 RETURN_DEL`: killed by every two-channel classifier call, because unpacking None raises TypeError.
- `custom_components/heatpump_optimizer/thermal_model.py:1218 RETURN_DEL`: killed by every classifier call, because a None draw reaches `idle_codes`.

## Red checks

Read from the whole check-run set of PR #3184 at c34999c1dd512e45fea3027bc49da31a78050d8a, the PR head this repair starts from (54 runs, one page of 100, read 2026-11-04 by `get_check_runs`). The new code head has no CI yet: a handoff ref runs no job. Every concluded red at c34999c1:

- `tests / mutation` (job 126509242207): `MUTATION TABLE REFUSED` on the 8 added unpinned sites. The bot's pin run pinned seven; the eighth, `freq_control.py:228 GUARD_OFF`, survived because the check the earlier body named did not kill it. Repaired here: a new check kills it and the pin json is committed (`## Mutation proof`).
- `gate` (jobs 126520080238 and 126519094366, two runs): the required aggregate, red because `tests / mutation` and `pr-contract / pr-contract` are red below it.
- `pr-contract / pr-contract` (jobs 126519711082 and 126518787652): `ERROR [pr-body] the red history could not be derived: check-runs at e3daad4: HTTP 502 from /repos/tvofi/heatpump_optimizer/commits/e3daad4d2c08317cb061606dacf45f9a059cb64c/check-runs`, a transient HTTP 502 reading check-runs, and nothing else red in that job (`CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)` in the same log). A re-run is the proof; this body changes nothing it reads from a 502.

Reds on ancestors of this head, read from the check-run sets of 913e74e8 and c34999c1 (the ancestry), each answered:
- `tests / mutation-autofix` (red at the bot head): the autofix job went red by design because its applied measurement left `freq_control.py:228 GUARD_OFF` alive (`ci-autofix.md`: a survivor is red; triage is manual). Answered by the repair: the new check kills the site and the pin json is committed.
- `tests / replay`: 1 of 176 replay checks FAILED, `synthetic-dhw-only.json: cycle_cost [cpu_ratio 2.825 over its budget 2.173]`. Timing noise on a shared runner: the review measured the fixture at base (`cpu_ratio 2.553`) and at head (`2.455`), both over 2.173, so the base fails the same way and the red is the runner's. The diff touches no replay code or budget; no cheaper detector exists than the replay lane itself, whose standing cost is its own minutes. It is skipped at c34999c1.
- `tests / nightly-status`: the unrequired nightly lane, red on the default branch's nightly. This diff touches neither nightly.yml nor that lane, so the red is the orchestrator's on `main` (`defect-root-cause.md`).

The branch also turned three checks red in the local scoped gate at b03b76d5d, all fixed before the first handoff:
- **typing_ruler** (`attr-defined` +5). Importers took `FREQ_MODE_*` from `freq_control` after it began importing them from `const`, which is an implicit re-export. The cheaper detector is the source-only typing ruler: it runs mypy, takes about a minute, and is run_always. No cheaper one exists for re-export semantics.
- **stress** (`winter_extreme/2z/space`, "1 heating steps have no reason code"). The invariant was a copy of the retired 0.05 line. A cheaper detector would be the P2 registry extended to `tests/`. It does not exist, because the registry reads production modules only. Recorded refusal: tests are not production deciders, and the stress sweep runs on every scoped diff that touches the optimizer.
- **harness_headers** (canonical `repo_root` walk). The new harness's copy lacked the inner import. The cheaper detector is harness_headers itself, about 10 s and run_always.

The mutation red is also one a cheaper detector could have run: `python3 tests/mutation_table.py --pin-killed --base origin/main` is the lane's own command and ran here in minutes; the fixer's miss was naming a killer check without mutating the site in isolation (`fixer.md` step 2), now done.

## Forward-carry

none

## Friction

none
