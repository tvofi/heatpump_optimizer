R10-RATIO-ANCHOR: the thermal-learning store now records the lower nameplate the learned lower-floor ratio multiplies, and the power basis the heat-loss learners replayed. On load and on a snapshot restore, `reanchor_heat_loss` (thermal_model.py, pure) re-expresses the scale and the ratio together under the #86 law, held on the zone total with the scale's confidence and on the lower zone with the ratio's. A power meter added since the save voids both learners' evidence (G-ID-3), so the law runs at zero confidence and both land on the configuration. Part of #2239 (D12-s2-71, with G-ID-3 from the identifiability study). This group's `fixes` list is empty, so the pull request closes nothing by keyword and leaves #2239 open: the class issue still carries D7-s2-58 and two beyond-finding sweep seams (below).

Decisions:

- **The architect note's "re-anchor at the write of the prior" is read as the existing anchor mechanism, not as a `config_flow.py` hunk.** The options flow writes the nameplate and reloads the entry. The first point that sees both the stored learners and the new nameplate is `_async_load_thermal_learning`, and the snapshot restore (`_apply_learner_payloads`) is the second route to the same misattribution. A re-anchor inside the options-flow save would be a second mechanism beside #86's anchor-on-save, re-anchor-on-load (`fixer.md` step 17: "the existing mechanism, never a parallel one"), and it would leave the snapshot route open. The diff touches no `config_flow.py` line and adds no coordinator attribute: `coordinator_attrs` is unchanged against main (`tests/structure.py`). The orchestrator may judge this reading a departure from the note. If so it is raised here, not made silently.
- **The ratio is re-anchored only when the nameplate split moves past `HOUSE_LOSS_MAX_STEP`** (`heat_loss_anchor_pair`). At partial confidence the law blends toward the nameplate, so re-anchoring a ratio whose split did not move would pull the lower zone off its measurement. The check `an edit that keeps the nameplate split keeps the ratio and each zone` pins this, and mutant D reddens it.
- **G-ID-3 voids rather than rescales.** Evidence fitted on commanded power carries every delivery shortfall into the scale, and nothing in the store separates the shortfall from the envelope. The law at zero confidence is the configuration, as for an install that has learned nothing. A move to an earlier basis, metered to commanded, keeps the evidence (`removing the power meter keeps both learners verbatim`). A store written before the basis was recorded proves nothing about it, so it adopts the configured basis and voids nothing (`a store without a recorded basis keeps both learners on a meter add`).
- **Clamp means reset, consistently** (this seat's commit `b49602160`, on top of the earlier seat's commits that this branch carries). A ratio whose re-anchor leaves `[LOWER_FLOOR_LOSS_RATIO_MIN, LOWER_FLOOR_LOSS_RATIO_MAX]` already reset to 1.0 with its samples zeroed. The scale beside it, however, kept the value solved jointly with the inexpressible ratio. `reanchor_heat_loss` now owns that reset (`ratio_bounds`) and solves the pair again at zero ratio confidence. That is the same landing as a store whose ratio never learned, pinned by `the scale beside a reset ratio is the scale with no ratio evidence`. Alternatives: (a) keep the jointly solved scale, which was the defect; (b) solve again in the coordinator, which added one logic statement and turned `coord_footprint` 2470 -> 2471, a gate rise `tools/audit/archscore/score.py --diff` refused. The pure-function form keeps the computation out of `coordinator.py` (step 17) and the score at NULL.
- **The finder's harness no longer runs at main** (`learner_newton_step` lost its `max_step_fraction` keyword, section 5). `dev/audit/harnesses/r10_ratio_anchor.py` keeps its options-reseed and snapshot arms runnable in the tree, and adds the split-kept and meter-add arms (`fixer.md` step 18).

## Head

`97ce097abeb43faeea0d7c071ee42d574705eeea`. Its merge base with `origin/main` is `50af6174f53c0f9bec3f705c3a4bb99615f71acc`, which was also `origin/main`'s tip at 2026-10-24T09:08:14Z. The branch is cut from that tip and merges the earlier seat's unreturned `handoff/r10-ratio-anchor` head `db35c6c43` (cleanly, no conflict resolution), so the push fast-forwards that ref. On top of that merge come one fix commit and one budget re-record. Every figure below was taken at this head and, where it says so, at the merge base.

## Mutation proof

Each mutant is a worktree at the head with one production line changed, followed by `PYTHONPATH=tests/hastub python3 tests/features.py`. Unmutated, the head prints `ALL 4362 FEATURE CHECKS PASSED`.

- **A**: delete `self._apply_lower_floor_loss_ratio(new_ratio)` in `_reanchor_house_heat_loss_scale` (the ratio is no longer re-anchored). Result: `6 of 4362 FEATURE CHECKS FAILED`: `a two-zone edit re-anchors on the zone total, not the upper zone`, `an options reseed of both zones keeps each zone's learned heat loss`, `a pre-reseed snapshot restored after the reseed keeps each zone`, `an inexpressible ratio resets, not clips onto a bound`, `the scale beside a reset ratio is the scale with no ratio evidence`, `adding a power meter re-anchors both learners at zero confidence`.
- **B**: replace the body of `if void:` (the samples zeroed) with `pass`. Result: `1 of 4362`: `adding a power meter re-anchors both learners at zero confidence`.
- **C1**: replace `reanchor_heat_loss`'s `if b and not ratio_bounds[0] <= new_ratio <= ratio_bounds[1]:` with `if False:`. Result: `2 of 4362`: `an inexpressible ratio resets, not clips onto a bound`, `the scale beside a reset ratio is the scale with no ratio evidence`.
- **C2**: replace the reset's re-solve with `return new_scale, 1.0, True` (the behaviour before this seat's commit). Result: `1 of 4362`: `the scale beside a reset ratio is the scale with no ratio evidence`.
- **D**: replace `heat_loss_anchor_pair`'s split gate `if void or abs(now[1] * then[0] / (now[0] * then[1]) - 1.0) > step:` with `if True:`. Result: `5 of 4362`: `and a second load over the reseeded configuration re-anchors nothing`, `an edit that keeps the nameplate split keeps the ratio and each zone`, `a metered store reloaded metered keeps both learners verbatim`, `removing the power meter keeps both learners verbatim`, `a store without a recorded basis keeps both learners on a meter add`.

Each mutant was restored by removing its worktree. `stress.py` was not run per mutant; that is left to CI's required mutation check (`fixer.md` step 2).

## Null control

- The finder's perturbation: `--ratio 1.0` on both harnesses, at the merge base and at the head, reads `0.0000` on every zone row, both zones (the brief's forward-carried null). With no learned split there is nothing to misattribute.
- The finder's null: `--scale 1.0 --ratio 1.0` reads `0.0000` on every row at both ends.
- The split-kept edit (`reseed_split` in the in-tree harness, `options_reseed_upper_only` in the finder's) reads `0.0000` at the merge base and at the head. The defect needs the split to move, and the fix leaves that edit alone.
- The meter-add arm's controls are features checks, green at the head: a metered store reloaded metered, the meter removed, and a store with no recorded basis all keep `(scale, ratio)` verbatim.
- Unmodified tree: the merge base reads the defect on the same command (`## Figures`).

## Figures

Both harnesses were run from the repository root as `PYTHONPATH=tests/hastub python3 <harness> [args]` in a detached worktree of `50af6174f` (base) and in this head's worktree (head).

- Finder's harness, `$EXPORT/tools/audit/round10/study-reseed/reparam_sites.py` (`git show 2c42ba4a0:tools/audit/round10/study-reseed/reparam_sites.py`, sha1 `0536f495b368e23b8afdd2620a9085afa6afcf0a`). It raises `TypeError: learner_newton_step() got an unexpected keyword argument 'max_step_fraction'` in section 5 at both ends. It was therefore run as a copy with section 5 deleted (from its `# --- 5. the learner step` line up to `# --- 6. reseed through the OPTIONS path`), sha1 `e32872268b4732896b986f581e26972db8d3dcc0`; sections 6 and 7 are unchanged.
  - Base: `options_reseed_both_zones.upper_rel_err=0.3681`, `.lower_rel_err=0.2145` (`scale 0.632 ratio 1.922`), `.house_rel_err=0.0011`; `snapshot_restore_after_reseed.lower_rel_err=0.2145`.
  - Head: those four rows read `0.0000` (`scale 1.000 ratio 1.000 samples 310/147`).
  - `--ratio 1.0` and `--scale 1.0 --ratio 1.0`: every row `0.0000` at both ends.
- In-tree harness, `dev/audit/harnesses/r10_ratio_anchor.py` (sha1 `602876e41a327f9d97ed2a4d4ba16c3e97d8e64c`; copied byte-identical into the base worktree for the base run).
  - Base: `reseed_both.upper_rel_err=0.3681`, `.lower_rel_err=0.2145`; `snapshot.upper_rel_err=0.3681`, `.lower_rel_err=0.2145`; `reseed_split.*=0.0000`; `meter_add.scale=1.5670 ratio=1.9220 samples=310/147`.
  - Head: every zone row `0.0000`; `meter_add.scale=1.0000 ratio=1.0000 samples=0/0`.
  - `--ratio 1.0`: every zone row `0.0000` at both ends.
  - `--scale 1.0 --ratio 1.0`: every zone row `0.0000` at both ends, and `meter_add` at `1.0000/1.0000` at both ends (its samples void to `0/0` at the head by design).
- Both ends of the input range (`fixer.md` step 3), as features checks green at the head:
  - Zero evidence: `an unlearned install keeps a lower-nameplate edit`.
  - The clamp: `an inexpressible ratio resets, not clips onto a bound` and `the scale beside a reset ratio is the scale with no ratio evidence`.
- The class's seams (`fixer.md` step 8). Instrument: #2239's own enumerator, `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P3/enumerate.py --tree <checkout>`. Its arm A is the rule for this fix: every `store.DOMAINS["thermal_learning"]` key ending `scale` or `ratio` with no sibling `*_anchor` key sharing its stem.
  - Base: `R=3 S=4 A=3 F=9`. Head: `R=4 S=4 A=2 F=9`.
  - `--null`: `R=0 S=0 A=0 F=1`. `--perturb` at the head: `perturb_delta R=1 A=1 (expected 1 and 1)`.
  - Arm A's seams at the head, each with its disposition:
    - `house_heat_loss_scale`: anchored, already guarded (#86).
    - `lower_floor_loss_ratio`: anchored, closed in this diff.
    - `cop_scale`: NO-ANCHOR. A distinct seam already recorded on #2239's sweep table as beyond-finding, not this group's. Carry: #2239
    - `solar_aperture/scale`: NO-ANCHOR. Same disposition; a re-measure at this head on the real coordinator reads the stored scale `1.500` kept verbatim over a `window_area` edited 18 -> 27, the sweep's `0.5000`. Carry: #2239
  - Arm R's one new seam is `_heat_loss_anchors`' raw `lower_floor_heat_loss` read. It is the anchor itself: the prior is recorded unmultiplied by design, so this is not a seam of the class. The remaining R and S seams are unchanged from the base and belong to D2-s1-71 (landed by R10-RATIO-SITES) and the refuted D2-s3-73.
- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 30 script(s) run, 3 scoped out.` (SCOPED, so the count is meaningful). `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` hit this seat's 30-minute background limit after `arch_score_head.py` started. Every script it finished passed, except `tests/entities.py` (the container trap below).
  - The four scripts it did not reach or failed were run by hand at the head: `tests/arch_score_head.py` rc 0; `env -u BASH_ENV python3 tests/entities.py` printed `ALL 2425 ENTITY CHECKS PASSED`; `python3 tests/gate_lock.py auto-lease --label <seat> -- python3 tests/stress.py` printed `ALL 113 STRESS CHECKS PASSED`; `tests/harness_headers.py` printed `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `tests/golden.py` is skipped by `GOLDEN_MODE=drift`, and `tests/env_drift.py` passed in the gate.
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: no breach against the re-recorded file.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed `no closures or fast red predicted against 50af6174f53c` and 27 unpinned sites (`## Unpinned sites`).

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main HEAD` printed `Architecture score: dS +0.0000 NULL`: admissible, with no metric rising.

## Structure budgets

Re-recorded from `origin/main`'s budget file at the merge base (`tests/structure.py --record`, the reason in commit `97ce097ab`). `class_excess_loc` and `max_class_loc` each fall by 3 against main, because the law's computation moved out of the coordinator class into `thermal_model.py`. Every other row is unchanged, and no row rises against main, so no raise is asked.

## Unpinned sites

The predictor's 27 keys, by `file:line KIND`. "Pinned by mutation-autofix" means CI's `mutation-autofix` pins each killed mutant (`ci-autofix.md`); a survivor it reports is triaged by hand, never by automation.

- `custom_components/heatpump_optimizer/coordinator.py:5126 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:5130 GUARD_OFF`: pinned by mutation-autofix; the same branch emptied (mutant B under ## Mutation proof) reddens `adding a power meter re-anchors both learners at zero confidence`
- `custom_components/heatpump_optimizer/coordinator.py:5137 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:5144 CMP_BOUND*2`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:5144 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1413 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1419 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1419 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1419 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2028 CLAMP_DROP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2028 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2028 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2031 CMP_BOUND*2`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2031 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2033 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2033 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2035 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2035 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2035 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2037 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2084 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2085 CMP_BOUND*2`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2085 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2088 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2088 CMP_BOUND*2`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:2088 GUARD_OFF`: pinned by mutation-autofix; the same predicate forced false (mutant C1) reddens two checks under ## Mutation proof
- `custom_components/heatpump_optimizer/thermal_model.py:2090 RETURN_DEL`: pinned by mutation-autofix

## Red checks

none on this branch: no pull request exists yet, and a handoff ref runs no job. `main`'s push CI is red on `tests / ci-ratchet`, which is the orchestrator's (a hotfix is in flight); this diff does not touch `tests/ci_ratchet.py` or anything it reads.

## Forward-carry

- R10-HEAT-METER (not started) wires the heat-meter add to this mechanism. The mechanism is the ordered tuple `HEAT_LOSS_BASES` in `const.py`, with `heat_loss_basis` and `heat_loss_basis_voids` in `thermal_model.py`. A later basis appended to the tuple voids evidence on every earlier one at the next load, and a move back to an earlier basis keeps it. The control that separates the real thing from its imitation is the features check `adding a power meter re-anchors both learners at zero confidence`, against its nulls `a metered store reloaded metered keeps both learners verbatim` and `a store without a recorded basis keeps both learners on a meter add`; mutant B (above) reddens the first alone. Re-measure at that group's own merge base. This seat may push only its return refs, so the orchestrator writes this line into R10-HEAT-METER's roster brief on `handoff/audit-r10-roster`. Carry: R10-HEAT-METER
- The adopt-learned-values options step (G4) is offered only after this group lands, and is not a card button. This is already in the roster's carry for this group; this pull request adds nothing to it. Carry: dismissed: already carried on the roster, not a new finding
- Lead for the sysid stage (fails safe, not owed): at scale 1.3 with a ratio of at least 1.2, the production experiment aborts as drifted beyond its excursion. Not re-measured here; this diff does not touch `sysid.py`. Carry: dismissed: inherited lead, not this seat's measurement

## Friction

- gate-scoping.md: cost: the scoped gate selects 30 scripts here, and its wall time exceeds a cloud seat's 30-minute default background limit, so the run was stopped after `arch_score_head.py` started and its remaining scripts were finished by hand. The `env -u BASH_ENV` trap for `tests/entities.py` is already in `tools/audit/seat/INSTRUMENTS.md` (`cloud_dispatch.py`'s entry); `run.sh` does not apply it, so the gate's own entities run fails the two shell-step checks that plant a fake `python3` on `PATH`. Carry: dismissed: a seat-side timeout and a documented trap, no tree change owed by this group
