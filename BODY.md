R9-UX-10: where the water flow meter is the install's signal, the house and lower-floor heat-loss learners replay the metered heat instead of the commanded power.

Closes #2016

**Stacked on R9-UX-9 (#2024).** This head is cut from `handoff/r9-ux9` at 543393cc, the authored code head of #2024's approved head 65f5e914. The diff against `origin/main` therefore carries #2024's 33 files too. This PR's own diff is `git diff 543393cc..HEAD`: 7 files. #2016 items 1-3 are #2024's. Item 4 is this PR. Retarget or update this PR from `main` only after #2024 merges.

Before this change, an install with no power entity replayed the **commanded** electrical power through the modelled COP in `_async_learn_house_heat_loss` and `_async_learn_lower_floor_loss`. A pump that did not deliver its plan, or a COP curve that does not match the machine, was then blamed on the heat-loss coefficient.

- `flow_meter.flow_is_signal(config)`: the flow meter is the signal when its key holds an entity and neither a power nor a frequency signal outranks it (the #1955 probe; #2016's rule). It is refactored out of `read_heat_output_kw`, which now calls it.
- `flow_meter.learner_power_kw` and `replay_heat_kw`: where the meter is the signal, the replay gets `0.0` kW electrical and the metered kW as the step's free-heat input. That input joins the hydronic mix exactly like the pump's own heat, so no COP stands between the meter and the fit. These intervals are no sample:
  - an unreadable reading (stale, negative, unavailable, unknown unit, crossed probes). This follows the stale power meter's rule and never falls back to the commanded guess.
  - a planned hot-water share.
  - an observed mode that heats no rooms.

  A two-tank plant keeps the commanded figure, because its free-heat input charges the wood tank and the step has no route for the pump's metered heat there.
- `_interval_space_power` routes to it when there is no power entity. Both learners pass `external_heat_kw=replay_heat_kw(...)` to their `simulate_step` replay.
- With the flow key unset, `flow_is_signal` is False and the learners get the same `(commanded, 0.0)` inputs as before.

Design alternatives (fixer.md step 17):

- **Dividing the metered heat by the step's COP** (keeping an electrical-only replay). This was the first design, and the failing test committed first (4dae0b32) assumed it. It was measured and rejected. On a throttled two-zone plant with the Carnot lift, the tank warms through the step's stability sub-steps (8 at 0.25 h, 44 at 1.5 h). So a fixed electrical figure replays a declining heat, and the upper floor misses by up to 0.16 K over one sample. The test now pins the replay against an oracle: the same step with its COP fixed at exactly 1, fed the heat as electrical power.
- **A tuple return from `_interval_space_power`**. Rejected because `tests/dst_checks.py`, `tests/features.py` and `dev/audit/harnesses/scale_writer_seams.py` replace the method with float-returning lambdas.
- **Deduplicating the two learners' replay blocks**. Rejected because `tools/audit/archscore/planted/perturb/G2_dedupe.py` plants exactly that dedupe as the archscore's perturbation.

Judgements, recorded so a reviewer can contest them:

- **Frequency outranks the flow meter, as #2016 says.** On a frequency-only install (no power meter), the learners still replay commanded power, since frequency gives them no power figure (the frequency map learns only alongside measured power). The flow meter would be the better input there. The precedence was kept to the issue's rule and UX-9's published attribute.
- **The COP learner is not fed.** `_learn_measured_cop` needs measured electrical input. Metered heat divided by commanded power would book tracking error as efficiency, which is the v4.0.5 failure that learner's gate exists for.
- **Not clamped at nameplate.** A heat far above nameplate is replayed as measured. Bounding one sample is the learner trust region's job (`learner_newton_step`), downstream.
- **No optimality claim.** No price, plan or solve is touched, so no flat-price control is owed.

Ratchet: paid, not raised.

- `max_class_loc` goes from 9049 to 9047. The feature's code adds 6 lines to the class (`git diff 543393cc..HEAD -U0` on `coordinator.py`). To pay for them, the docstring hunk of `_interval_space_power` goes from 16 lines to 8, which includes the new flow-meter sentence: its v5.3.0 paragraph restated `_commanded_split`'s own docstring and is cut to a pointer.
- `seam_cut_total` goes from 768 to 767. `_interval_space_power` moves from the `grid` seam to `learning` in `tests/seam_map.json`. Its only callers are the two heat-loss learners, and it is their input. The move alone measures 764 at the base (-4); the feature costs +3.
- Both rows were re-recorded downward in eeeec50e, with the reason in its commit message. Both stay under #2024's raised caps (9049 / 768). Against main's caps (9048 / 766), `seam_cut_total` is +1 only because #2024's approved +2 raise is in this stacked diff.

## Head

bcbc1af3ba3d3bd735ade24b9afe3c29c1738695

Stacked on 543393ccafabd6bac34898248a71361f67329b29 (`handoff/r9-ux9`, the authored head inside #2024's approved head 65f5e914b91ed64583c978e2074f8a5a4b973883). Merge base with `origin/main`: 2d8cab3f75ddc8c2e42877092cd14bd1ffb01d38. Commits: 4dae0b32 (failing test), 9e40fec2 (fix, test redesigned), eeeec50e (ratchet re-record), bcbc1af3 (docs).

## Mutation proof

The full `tests/features.py` belongs to CI. Locally, the new checks were run through an extract: `tests/features.py` lines 1-159 (imports, `R`, `NOW`) plus everything from the `#1956 the card recommends` block to the end of the file. That covers #2024's flow checks, whose `_fm_reader` the new block reuses, and the 10 new checks. A scratch driver applied each mutant, ran the extract with the venv-ci Python 3.14 (`PYTHONPATH=tests:tests/hastub`), and restored the file. Null M0 (no mutation): rc 0, `ALL 29 FEATURE CHECKS PASSED`.

Mutants on the precedence rule and on the stale/negative path:

- M1 `flow_is_signal`: `cap.measured_power or cap.frequency` changed to `cap.measured_power`. KILLED: "a frequency sensor or entity outranks the flow meter: the learner keeps the commanded figure and no metered heat", plus #2024's "a power or a frequency signal keeps the estimate off".
- M2 the same, changed to `cap.frequency`. KILLED: "a power or a frequency signal keeps the estimate off (the signal outranks the flow meter)".
- M3 `learner_power_kw`: `heat_kw is None` dropped. KILLED: "a negative, unavailable, stale or unknown-unit flow reading gives the learner no sample rather than the commanded figure".
- M4 `dhw_share > 0.0` dropped, and M5 the no-space-heat mode clause dropped. Each KILLED: "a planned hot-water share or a mode heating no rooms is no sample; `heat` with a phantom share still teaches".
- M6 the two-tank power gate dropped, and M7 the two-tank heat gate dropped. Each KILLED: "a two-tank plant, whose free-heat input charges the wood tank, keeps the commanded figure and is fed no metered heat".
- M8 the coordinator's flow branch disabled (`if True`). KILLED, 5 checks, including "a planted 15 L/min over a 5 K drop reaches both heat-loss learners as 5.2220 kW of heat and no electrical power" and "on every plant the step distinguishes, the learner's replay delivers exactly the metered heat, up to a heat far past nameplate".
- M9 the house learner's `external_heat_kw=` line deleted, and M10 the lower-floor learner's line deleted. Each KILLED: the planted check.

The mutation lane's own operators (`mutation_table._generate`) were also run at the 7 sites this PR adds (`## Unpinned sites`). All 7 were KILLED. `flow_meter.py:94 RETURN_DEL` is killed by a TypeError in the check: the replay is handed `None` heat.

## Null control

The unmodified tree here is the stacked base 543393cc. The new block was run against its production code, with `replay_heat_kw` (absent there) shimmed to the base's behaviour of no free heat. Result: rc 1, 5 of 29 failed:

- the planted check (`[(3.0, 0.0), (3.0, 0.0)], want (0.0, 5.222035) twice`)
- the unreadable-reading check (each case `[(3.0, 0.0)]`)
- the zero-flow check
- the hot-water/mode check (`(3.0, 0.0, 3.0)`)
- the oracle check (worst 38.6 K, two zone with valve and Carnot lift, 2.0 kW, 1.5 h)

The controls pass at both ends:

- "null control: with the flow key unset both learners replay the commanded 3.0 kW and no free heat, the inputs they had before" passes at the base and at this head. With the key unset, both learners' replay inputs are the same `(3.0, 0.0)` at both trees.
- The precedence checks pass at both trees.
- "a power meter outranks the flow meter" passes at both trees.

The oracle's own null: "null control: the commanded 3.0 kW replayed through the COP misses the metered heat on every plant by more than the oracle's tolerance" passes, so the oracle tells the two inputs apart.

Golden fixtures: this PR claims nothing. `git diff 543393cc..HEAD -- tests/golden/` is empty. The `claimed_drift.txt` change in the diff against `main` is #2024's six R9-UX-9 claims. No golden configures `flow_meter_entity`, and with the key unset the learners' inputs are identical, as above. `GOLDEN_MODE=drift` is CI's (`golden.py` is a heavy script).

## Figures

At bcbc1af3 unless stated. Interpreter: `~/.local/state/hpo/venv-ci/bin/python3` (3.14), `PYTHONPATH=tests/hastub`. Heavy scripts (`features.py`, `golden.py`, `stress.py`, `optimality.py`, `boost_drift_replay.py`, `arch_score*`) are CI's and were not run.

- `python3 tests/structure.py`: rc 0, `STRUCTURE RATCHET PASSED` (`max_class_loc` 9047, `seam_cut_total` 767).
- `python3 tests/entities.py`: rc 0, `ALL 2204 ENTITY CHECKS PASSED`.
- `python3 tests/harness_headers.py`: rc 0, `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/doc_claims.py`: rc 0, `ALL 160 checks PASSED`.
- `python3 tests/typing_ruler.py`: rc 0. `python3 tests/guard_pins.py`: rc 0. `node tests/md_tables.mjs`: rc 0, `doc_misrendered_lines=0`.
- The features extract described under `## Mutation proof`: rc 0, `ALL 29 FEATURE CHECKS PASSED`. At 543393cc it gives rc 1, 5 failed (`## Null control`).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: `MODE: SCOPED -- 31 script(s) run, 2 scoped out` (`ha_contract.py`, `layout.py`).
- `python3 tools/pr/ci_predict.py --base origin/main`: rc 0, `no closures or fast red predicted against 2d8cab3f75dd`, and 18 ADDED UNPINNED sites. 11 are #2024's; 7 are this PR's.
- `python3 tools/pr/ci_predict.py --base origin/handoff/r9-ux9`: rc 0, `no closures or fast red predicted against 543393ccafab`, and the 7 ADDED UNPINNED sites listed below.
- The Carnot-plant figure (up to 0.16 K at the upper floor, divide-by-COP design): a scratch probe over tank 35/48/60 °C x heat 2.0/5.22/9.0 kW x dt 0.25/1.0/1.5 h. It compared `simulate_step(state, Q / COP)` against `simulate_step(state, 0, external_heat_kw=Q)` at 9e40fec2's parent tree. The worst cell, `upper_floor_temperature`, was 0.1639 K at a 60 °C tank, 2.0 kW, 1.5 h. Single-zone and no-valve plants were 0.0 in every cell.

## Unpinned sites

The 7 sites this PR adds (`ci_predict.py --base origin/handoff/r9-ux9`). Each is killed locally by the lane's own operator (`## Mutation proof`), and each is to be pinned by `mutation-autofix` once CI runs on the PR. Nothing is pinned locally (`ci-autofix.md`).

- custom_components/heatpump_optimizer/coordinator.py:4351 GUARD_OFF: killed by the planted check and 5 others; pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_meter.py:73 GUARD_OFF: killed by the two-tank check; pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_meter.py:77 CMP_BOUND: killed by the hot-water/mode check and the planted check; pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_meter.py:78 BOOLOP: killed by the hot-water/mode check; pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_meter.py:81 RETURN_DEL: killed by the planted, zero-flow and hot-water/mode checks; pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_meter.py:94 RETURN_DEL: killed (TypeError in the check); pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_meter.py:108 GUARD_OFF: killed by both precedence checks; pinned by mutation-autofix

The other 11 sites in the diff against `origin/main` are #2024's. They are dispositioned in #2024's body (all pinned by mutation-autofix, awaiting R9-CI-1), and this PR does not touch their lines:

- custom_components/heatpump_optimizer/flow_meter.py:32 GUARD_OFF: #2024's (its :31, moved one line by this PR's module docstring); pinned by mutation-autofix, awaiting R9-CI-1
- custom_components/heatpump_optimizer/flow_meter.py:37 CMP_BOUND: #2024's (its :36, moved likewise); pinned by mutation-autofix, awaiting R9-CI-1
- custom_components/heatpump_optimizer/inputs.py:278 GUARD_OFF: #2024's; pinned by mutation-autofix, awaiting R9-CI-1
- custom_components/heatpump_optimizer/inputs.py:281 RETURN_DEL: #2024's; pinned by mutation-autofix, awaiting R9-CI-1
- custom_components/heatpump_optimizer/inputs.py:821 GUARD_OFF: #2024's; pinned by mutation-autofix, awaiting R9-CI-1
- custom_components/heatpump_optimizer/inputs.py:825 CMP_BOUND: #2024's; pinned by mutation-autofix, awaiting R9-CI-1
- custom_components/heatpump_optimizer/inputs.py:825 GUARD_OFF: #2024's; pinned by mutation-autofix, awaiting R9-CI-1
- custom_components/heatpump_optimizer/inputs.py:827 GUARD_OFF: #2024's; pinned by mutation-autofix, awaiting R9-CI-1
- custom_components/heatpump_optimizer/inputs.py:831 RETURN_DEL: #2024's; pinned by mutation-autofix, awaiting R9-CI-1
- custom_components/heatpump_optimizer/inputs.py:833 RETURN_DEL: #2024's; pinned by mutation-autofix, awaiting R9-CI-1
- custom_components/heatpump_optimizer/thermal_model.py:1286 RETURN_DEL: #2024's; pinned by mutation-autofix, awaiting R9-CI-1

## Red checks

CI has not run on this head: it is a handoff ref, and no PR is open. `ci_predict.py` predicts no closures or fast red against either base. One red is predicted:

- `budget-raise-gate`, predicted by `prepr.sh`'s pr-body step. Against `origin/main`, `tests/structure_budgets.json` moves `seam_cut_total` from 766 to 767. That rise is #2024's approved raise (766 to 768, tvofi 2026-10-07, for the flow-meter key) inside this stacked diff, lowered here to 767. This PR's own change (543393cc..HEAD) lowers both rows: 768 to 767 and 9049 to 9047. Once #2024 merges and this branch is updated from `main`, the diff against `main` raises nothing and the gate has nothing to refuse. No cheaper detector exists for "a human approved this raise". `prepr.sh` itself is the detector that named it here, before any push.
- `mutation`: the 18 unpinned sites under `## Unpinned sites`. The 7 that are this PR's are killable by the checks named there.

## Forward-carry

none. The two judgements above (frequency-only installs keep the commanded replay; the COP learner is not fed) follow #2016's stated rule and change no later stage's work.

## Friction

none
