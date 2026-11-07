Fix review: merge d95f6b7a88e6c2d960ee897b915d4c7941b45de9

bus-nonce: b43f740a6e25c44517473f6305a9dc76

## Summary

Round 1 of the adversarial fix review of #3268 (R10-COMBI-TANK PR 0, R10-BUFFER-OPENLOOP), done from a detached worktree at `d95f6b7a88e6c2d960ee897b915d4c7941b45de9`. Merge base and origin/main are both `80016a71f567d936450d8708abcbb79d9e8071d7`, and `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

The production diff implements design `a605014b` §C0 and nothing more:
- `_seed_store(reading, result, trajectory_attr, now)` is one module-level primitive over `_open_loop_plan_value`.
- The DHW seed is re-expressed through it, and the buffer seed is added.
- In the observation split, the rise inputs take `reading.value if reading.ok else None` from the method's own `reader` (the `observation-read-in-place` note), and `hp_tank_temp` keeps its text and reads the seed.

Every quoted figure re-derives at both ends. Every mutant I planted is killed. The test fails first at base. The branch merges cleanly. CI at this head was never decided: the code run was cancelled when the bot's pin commit was pushed (see Evidence). That commit carries this verdict to `129dc30d`, whose own runs decide.

## Findings

- Follow-up: `## Red checks` spells the red as `mutation`, but the check is `tests / mutation`, and it does not name the concluded-red `gate` (edit run 42317532474, job 128234307691). `review_packet.py` refuses both as `red-unanswered`. The substance is answered: the three ADDED UNPINNED sites were predicted by `ci_predict` and are pinned by bot commit `129dc30d`. The fixer should spell the check names exactly, and should name the `gate` red as the edit-run deferral that run 42317532285 decided (later cancelled), so that `pr-contract` at the new head reads the body clean. The edit is body-only and does not move the head. Carry: R10-COMBI-TANK
- Follow-up: the `gate` red at this head is the edit-run gate deferring to the code run: `FAIL run(s) [42317532285] at this head are still being judged; their gate decides`. That run was cancelled at 01:16Z when `ci: pin killed mutants` was pushed, so this head has no deciding gate. `merge_train.py classify` printed `RED ... pending: none red: gate` on every poll from 00:29Z to 01:33Z (20 polls over 60 min). The run that decides is now the code run at `129dc30dfc100eac1ffb60f6047648b5607988ee`, which read `WAIT ... pending: gate red: none` at 01:37Z. This is the open gate-deferral class. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up: design `a605014b` §T.3 owes the energy-balance invariant `combi_energy_balance`, `|C·ΔT − RHS| ≤ 1e-9 kWh` over a 48-step `combi_tank_step` day, and its UA = 0 null control, which conserves `Σ(in − out)·Δt` to 1e-12 relative. PR 0 adds no heat-transfer path, no `combi_tank_step` and no `buffer_store_volume`, so the invariant has no code here to hold or fail. There was nothing to hand-derive or mutate at this head, and I did not build a stand-in. PR A must land it as a precondition, together with the double-count mutant the design names (capacity read from `buffer_tank_volume` on one side and `buffer_store_volume` on the other). Carry: R10-COMBI-TANK
- Follow-up: in combi, one buffer probe is the DHW water, but the DHW rise input added here reads only `CONF_DHW_TEMP_ENTITY` (`coordinator.py` `_update_external_heat_detection`, `dhw = reader.read(CONF_DHW_TEMP_ENTITY)`). On a combi install with only a buffer probe, the DHW rise detector therefore gets `None`. The body records this as a note for PR B but carries it nowhere, because combi is not reachable at this head and nothing can be measured. PR B's `combi_tank_seed` must decide the combi DHW rise input as a stated precondition, with an arm. Carry: R10-COMBI-TANK

## Evidence

- RESULT head=d95f6b7a88e6c2d960ee897b915d4c7941b45de9 (ev/HEAD.txt); merge base 80016a71f567d936450d8708abcbb79d9e8071d7 = origin/main.
- RESULT merge-tree: `git merge-tree --write-tree origin/main d95f6b7a…` gives rc=0 and tree d7e1b51623e7587becc74facaaa10e1a280e17e9, with no conflicts (ev/merge_tree.txt).
- RESULT head-moved-carry: the branch is now `129dc30dfc100eac1ffb60f6047648b5607988ee` (github-actions[bot], `ci: pin killed mutants`, 3 new killed_by pins, no other path). `review_carry.py d95f6b7a 129dc30d` prints `CARRY` (ev/review_carry.txt, ev/pin_commit.diff).
- Harness: `dev/audit/harnesses/r10_combi_tank.py`, sha1 7eb9b4b12c2fa83171e8d71fedf0d73b59f2b6eb. It is the fixer's own build, made to the design's spec: `a605014b` §Evidence plan names this file and the `no_probe` and `wood_seed` arms, and the design records that there is no finder harness, because the evidence is the owner report on #3225. I ran it at base (file copied in) and at head (ev/harness_base.txt, ev/harness_head.txt):
  - RESULT no_probe_seed: base 40.0,40.0, head 41.0,43.0.
  - RESULT no_probe_rise: base 40.0,40.0, head None,None.
  - RESULT wood_seed: base hp 40.0,40.0 / 26.6800 kWh / 0.5000, head hp 41.0,43.0 / 23.2000 kWh / 0.4444.
  - RESULT solve valve=manual: base seeds 40.0×4, head 40.0,42.5,40.9,40.3.
  - RESULT controls `no_probe probe`, `no_probe empty`, `wood_seed probe`, `wood_seed empty` and `solve valve=none` are identical at both ends, except the DHW rise input on a no-DHW-probe install, which moves 55.0 → None. That move is the fix.
  - Every figure in the body's Figures and Null control sections matches.
- Hand derivation (my own, from `external_heat.py` `_update_displacement`: floor = hp + 2.0 K, wood mean (70+60)/2 = 65 °C, 1000 L × 0.00116 kWh/(L·K)):
  - hp 43 gives (65 − 45) × 1.16 = 23.20 kWh, displacement (55 − 43)/(70 − 43) = 0.4444.
  - hp 40 gives 23 × 1.16 = 26.68 kWh and 15/30 = 0.5000.
  - probe 38 gives 25 × 1.16 = 29.00 kWh and 17/32 = 0.53125.
  - All three equal the harness output.
- Test design note: the `wood_seed` check computes its expected energy with the same formula as production, but what it actually discriminates is the `hp_tank_temp` input, which it also asserts directly. The `fixdel` and `noopenloop` mutants kill it, so it is not vacuous.
- RESULT features at head: `PYTHONPATH=tests/hastub python3 tests/features.py` gives rc=0, all 9 `R10-BUFFER-OPENLOOP` checks ok (ev/features_head.tail.txt).
- RESULT fail-first: head's `tests/features.py` run on base production code fails 4 of 4885 checks: the buffer level, the rise inputs, the DHW rise input, and `wood_seed` seed. This matches the body (ev/mut_failfirst.out).
- Mutants, each in its own worktree at the head and restored with `git checkout` (ev/run2.sh, ev/mut_*.out). All five are killed:
  - RESULT mutant fixdel (buffer seed back to `if buffer_reading.ok:`): 2 of 4885 FAIL, the buffer level and `wood_seed` seed, exactly the two the body names.
  - RESULT mutant riseseed (`buffer_temp=ctx._current_state.buffer_tank_temperature`): 1 FAIL, rise inputs carry no seed.
  - RESULT mutant dhwriseseed (`dhw_temp=ctx._current_state.dhw_temperature`): 2 FAIL, the rise inputs and the DHW seed reaching the state but not the rise input.
  - RESULT mutant predok (`reading.ok` → `False` in `_seed_store`): 3 FAIL. These are the buffer-probe null control, the `wood_seed` probe null control, and also the R9 `D12-s1-01: a mapped tank probe still wins the seed`. The body names the first two; the third confirms the DHW branch now shares the primitive.
  - RESULT mutant noopenloop (`_seed_store` returns `None` without a reading): 4 FAIL, among them the R9 DHW open-loop check and the buffer level.
- Robustness:
  - Restart with no history: the first solve has no plan, so the seed is `None` and the field keeps the 40.0 default (harness `solve`, first entry).
  - Missing trajectory: the `empty` arm keeps the level and never fabricates one.
  - Stale probe: `_rate` returns `(None, previous)` on `None` and does not overwrite the previous sample (external_heat.py:203-204).
  - The buffer-cooling learner is gated on `buffer_reading.ok` at coordinator.py:6679 and never reads the seeded state.
  - `_update_external_heat_detection` (6667) runs after the first publish (6613), so `hp_tank_temp` reads the seed.
- Observable effect beyond the body's list: on a no-probe buffer whose plan published a trajectory, the seeded `buffer_tank_temperature` now also reaches publish and stored-energy readers: `_thermal_view` (coordinator.py:7731), `battery.build` (battery.py:349) and `_stored_thermal_energy` (optimizer.py:5648). This is the intended consequence of the state carrying the best estimate, and the goldens do not drift (below).
- Integration efficiency: no solver code changes; only the seed value differs. Per tick the change adds two `InputReader.read` calls and one `_seed_store` call. RESULT bench (harness `cycles(wood=True)`, two ticks, 15 reps, interleaved, ev/bench.txt): base median 2.39 / 2.37 ms, head 2.28 / 2.39 ms. That is flat within noise; the second head sample overlapped a mutant run in a sibling worktree. No new per-solve allocation, no new loop, and no new coordinator attribute (`coordinator_attrs` 141 is unchanged).
- Architecture: one owner of the seed (`_seed_store`, module level) and no second source of truth. The rise inputs are read in place, as the design verdict asks. `hp_tank_temp` is unchanged, as §C0 decides. No logic was added in the sensor layer.
- Structure: RESULT `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED (ev/structure_head.txt). `max_class_loc` 7955 → 7954 and `class_excess_loc` 17585 → 17584 moved down and were re-recorded, earned by moving the seed body out of the class. No budget was raised; budget-raise-gate is success.
- RESULT claims: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 80016a71…` gives `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`, rc=0 (ev/env_drift.txt). Neither claim file is touched (checked three-dot).
- RESULT protected files: VERSION, manifest.json and RELEASE_NOTES.md are not in the three-dot diff.
- New tracked file: `dev/audit/harnesses/r10_combi_tank.py` is classified in `tests/closures.json`. The delivery row `dev/programme/delivery/3268.md` is in the diff.
- Flat-price null control: the PR states no savings figure, so none is owed.
- Class census: `git grep -n "_open_loop_plan_value(\|_seed_store(" -- custom_components` returns the primitive, its two calls, and the R9 slab site, matching the body's disposition. `ExternalHeatObservation(` has one construction, and its rise inputs are closed here.
- CI at this head (live check-runs, all pages, 46 runs at render and 52 later):
  - Concluded red: `gate` (edit-run deferral, see Findings) and `tests / mutation`. The mutation red is `MUTATION TABLE REFUSED -- 2942 unpinned site(s) against 2939 ... 3 of them added by this diff`, i.e. the three sites the body lists, pinned by bot commit 129dc30d.
  - Code run 42317532285 ended `cancelled`.
  - `merge_train.py classify` exited 1 (RED, `red: gate`) on every poll from 00:29Z to 01:33Z (ev/classify.rc). That RED is the deferral alone; per the orchestrator's note I do not block on it.
  - The new head reads WAIT (ev/classify_129dc30d.txt).
- Rounds: this is round 1.
