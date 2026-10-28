Fix review: merge 274e6975c1b7a4334d181879c4ad2bef532c4134

bus-nonce: 2e49347b2f3d48fa0489342a5a055b2a

Round 3 of #2698 (R10-RATIO-ANCHOR), the r3 return from the ratio-anchor-r2 fixer. It follows the block at `3383fb2ac` (bus-nonce `25b782df`). A fourth round would owe a re-cut, not a repair. Measured at head `274e6975c1b7a4334d181879c4ad2bef532c4134`, which is still the PR head and still `fix/r10-ratio-anchor` at verdict time. Measurements were taken from detached worktrees: the head; the PR merge base `5c0ee1093` ("base"); the head with origin/main `9d0ddf8af` merged ("merged"; it differs from the head only in five `dev/programme/delivery/*.md` files); and `b7c450091` ("pre-repair"). Roles diff `merge-base...origin/main -- dev/governance/roles/` was empty at the start. By verdict time origin/main had moved to `662a3809c`, which edits `fix-review.md`, `fixer.md` and `finding-propagation.md`. I read that diff and applied it. Its one rule this review turns on, step 6's "a site or a predicate's unguarded domain", is discussed under the flow-meter finding below.

## Findings

- **The R10-HEAT-METER forward-carry is not yet in that group's roster brief.** `handoff/audit-r10-roster` at `2124781cf` carries only "Adding the meter re-anchors the learner scales through R10-RATIO-ANCHOR's mechanism". It does not carry the control the body names: the ordered `HEAT_LOSS_BASES` tuple, the check `adding a power meter re-anchors both learners at zero confidence` against its two nulls, and mutant B reddening the first alone (`ev/roster-carry.txt`). The body says the orchestrator writes it, because the fixer pushes only return refs. `finding-propagation.md` requires it in the brief before this PR merges, so it is the orchestrator's to write before the merge, as the body's own text. Carry: R10-HEAT-METER
- **A flow-meter add moves the house learners onto measured heat, yet `heat_loss_basis` still reads `commanded`, so G-ID-3's void does not fire.** On main (#2016), `_interval_measured_heat_kw` (coordinator.py) feeds `flow_meter.read_heat_output_kw`'s kW into both learners' replay. That happens whenever `flow_meter_entity` is set and there is neither a power nor a frequency signal. `heat_loss_basis` keys only on `probe_install(...).measured_power`. Measured on the merged tree with the in-tree harness plus one `flow_add` arm (`ev/flow_probe.py`, the reviewer's own probe, not the finder's): `flow_add` reports `basis_before=commanded basis_after=commanded` and `scale=1.5670 ratio=1.9220 samples=310/147`, verbatim; the power-meter arm beside it reports `samples=0/0`. Null, `--scale 1.0 --ratio 1.0`: `flow_add` lands at `1.0000/1.0000` with nothing to keep (`ev/flow-meter-basis.txt`). The body's reasoning for G-ID-3 is "evidence fitted on commanded power carries every delivery shortfall into the scale". That applies as much to a commanded-to-measured-heat move by flow meter, so the basis predicate leaves this part of its domain unguarded.
  - Not blocked as `class-open`: the body names no enumeration rule for the basis class, its G-ID-3 source states one seam (power meter added), and the behaviour equals main's (no regression).
  - The precondition for the next stage: the basis that R10-HEAT-METER appends to `HEAT_LOSS_BASES` must also map the existing flow-meter route, or record why that route's evidence is kept. Control: this probe's `flow_add` arm against `meter_add`; re-measure at that group's merge base.

  Carry: R10-HEAT-METER
- **Clamp-reset upper-zone regression against main (the body's own first forward-carry, confirmed).** In the in-tree harness's two scale-reset rows, the measured upper zones are 50 and 40 W/K. Main keeps the scale at `0.3076` and `0.3037`, so the upper zone sits at 55.4 and 45.6 W/K. The head resets it to 1.0, so the upper zone lands on the new nameplate, 180 and 150 W/K. These figures are derived from my RESULT lines (`scale x 1.8 x 100 W/K`, `x 1.5`), not printed by the harness. The lower zone improves from pre-repair's 128.3/201.2 W/K to 40.6/60.2 W/K, against main's 31.0/52.5 W/K. Whether a joint solve leaving the scale's bounds should reset (the recorded #86 decision, applied consistently here) or fall back to the total-only law is an owner design call. The body carries it to R10-RATIO-ANCHOR, which this merge sets done, so that is no longer a destination. It needs a live owner of #2239 (R10-ARCH-SHAPES lists it). Carry: #2239
- The written triage `reanchor_heat_loss.CMP_BOUND.d73e7c95` (`lin <= 0` to `lin < 0`) says the two root forms part only at a zero total at full confidence. `const == 0` also holds at `b == 0`, `a == 1` or `lower == 0`. In each of those `lin` is strictly negative (`-(1-a)Q - a*total`, or `s*(l*r*(b-1) - u)` with `u > 1e-9`), so the forms never part there either, and the `equivalent` verdict stands. Carry: dismissed: verdict correct, reasoning gap only, no tree change owed

## Evidence

- RESULT merge: `git merge-tree --write-tree origin/main 274e6975c` exits 0 at `9d0ddf8af` (tree `6a1c3ccb9`) and again at `662a3809c` (tree `7ad002ef0`). There is no conflict, so the claim driver was not invoked (`ev/merge-tree.txt`).
- RESULT VERSION, manifest, `RELEASE_NOTES.md`, `tests/golden`: untouched in `merge-base...HEAD`. No claim file moves, so step 4 has no drift to compare.
- RESULT features prefix (lines 1-9065 plus `R.close`, as the body ran it): clean head `ALL 753 FEATURE CHECKS PASSED` (`ev/prefix-head-clean.txt`). Full `tests/features.py` on the merged tree: `ALL 4371 FEATURE CHECKS PASSED` (`ev/features-merged.txt`).
- RESULT mutation proof, every body mutant re-taken at this head as an exact one-site replacement that refuses a moved site (driver `ev/mut.py`, output `ev/mutants-prefix.json`). Each fails exactly the checks the body names, with the same detail strings:
  - E 3, F 3, G 3, H 1, A 8, C1 3, D 6 (including `split moved exactly step`);
  - B 1 and C2 1, both re-run here (the body carried them);
  - all eight boundary mutants 1 each, on their named case (the body did not re-run these; I did).
- RESULT my own mutants:
  - `(0.0, b)` to `(0.0, 0.0)` in the scale recursion: 2 failed;
  - the coordinator's `if ratio_reset:` to `if False:`: 2 failed;
  - `heat_loss_basis_voids`' `<` to `!=`: 1 failed (`removing the power meter keeps both learners verbatim`);
  - deleting the `l_now <= 0` guard: rc=1 by ZeroDivisionError;
  - `lin <= 0` to `lin < 0`: rc=0. It is the triaged equivalent above.
  - Dropping `a and` from the scale-reset predicate: rc=0. This is equivalent at the production bounds: at `a = 0` the root is exactly 1, inside `[0.3, 3.0]`, so the test cannot fire. The `a and` term only keeps a caller with bounds that exclude 1 from recursing without end.
- RESULT stale pins (the previous block): the three files `bc73e53b0` wrote (`..._reanchor_house_heat_loss_scale.GUARD_OFF.d4c65f00`, `reanchor_heat_loss.GUARD_OFF.7aabfa09`, `RETURN_DEL.1c6517e0`) are absent on the merged tree. `ci_predict.py --base origin/main` there prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 9d0ddf8afcb8`, with no STALE PIN line.
- RESULT ledger liveness: each of the diff's 29 `killed_by` files and its one `survivor_triage` file names an `old` line occurring exactly once in its file on the merged tree (`ev/ledger-pins-live.txt`).
- RESULT ledger kills: every one of the 29 `killed_by` anchors was driven by `tests/mutation_table.py --anchor`, against all of its sites (32 in all). All 32 were killed, with no survivor, and the `NULL_COMMENT` control survived each run (`ev/ledger-pins-anchor-runs.txt`). The driver was a byte-identical prefix of `tests/features.py` (lines 1-9065), registered under `features.py`'s recorded closure in a scratch worktree only, so the prefix's kill is a kill by checks `tests/features.py` runs first. One anchor, `heat_loss_basis RETURN_DEL 4a9b3d82`, was also driven with the named killer `tests/features.py` itself: `PIN RE-VERIFICATION: 1 reproduced`, baseline rc=0 in 352 s (`ev/anchor-full-features-heat_loss_basis.txt`).
- RESULT window-cache fixture (the previous block), on the merged tree:
  - `node tools/policy/policy_lint_mutants.mjs` exits 0 with `MUTANTS ok`;
  - `node tools/policy/policy_lint.mjs` exits 0 with `FIXTURE ok: 93 error(s) hold 258 pins` and no `window cache` line.
  - It is non-vacuous: with one planted perturbation, `cmdStats` passing `null` for its cache file, the same command exits 1 with `FIXTURE VACUOUS: window cache ["--stats --window-cache did not take commit-to-PR map and per-PR reads from the file"]`. That is the refusal text `prepr.sh` reported, and restoring the line restores rc=0 (`ev/window-cache.txt`).
- RESULT finder's harness `reparam_sites.py` (`2c42ba4a0`, sha1 `0536f495…`), run without section 5 (sha1 `e32872268…`, byte-identical to the body's; `ev/reparam_nos5.py`):
  - base: `options_reseed_both_zones.upper_rel_err=0.3681`, `.lower_rel_err=0.2145`, `.house_rel_err=0.0011`, `snapshot_restore_after_reseed.lower_rel_err=0.2145`;
  - merged: all four `0.0000`;
  - `--ratio 1.0` and `--scale 1.0 --ratio 1.0`: every row `0.0000` at both ends;
  - `options_reseed_upper_only.*` `0.0000` at both ends;
  - every figure equals the body's (`ev/finder-harness.txt`).
- RESULT in-tree harness `r10_ratio_anchor.py` (sha1 `14079faa…`), at base, merged and pre-repair (`ev/intree-harness.txt`):
  - base: `reseed_both` and `snapshot` `0.3681/0.2145`, `reseed_split` `0.0000`, `meter_add` `samples=310/147`;
  - merged: zone rows `0.0000`, `meter_add` `1.0000/1.0000 samples=0/0`.
  - `scale_reset` rows:
    - pre-repair `2.1586 (128.3 vs 40.6)` and `2.3431 (201.2 vs 60.2)`, ratios `2.7116/1.0127/1.6607 samples 0/147`;
    - head `0.0000 (40.6 vs 40.6)` and `0.0000 (60.2 vs 60.2)`, `1.0000 samples=0/0` in all three;
    - in-bounds null row `0.0037` at both pre-repair and head (main reads `0.0000` there, since it does not re-anchor the ratio).
  - Nulls `--ratio 1.0` and `--scale 1.0 --ratio 1.0`: zone rows `0.0000` at both ends.
  - Every figure the body quotes was re-derived.
- RESULT class (step 6): #2239's `enumerate.py`. Base `R=3 S=4 A=3 F=9`, merged `R=4 S=4 A=2 F=9`, `--null` `R=0 S=0 A=0 F=1`, `--perturb` `perturb_delta R=1 A=1 (expected 1 and 1)`. Arm A: `lower_floor_loss_ratio` turns `anchored`; `cop_scale` and `solar_aperture/scale` are `NO-ANCHOR`, dispositioned to #2239 in the body. The one new R seam is `_heat_loss_anchors RAW`, the anchor itself, as the body says. The clamp class's rule, `_bounds[` inside `reanchor_heat_loss`, returns the two sites, both closed.
- RESULT `tests/structure.py`: `STRUCTURE RATCHET PASSED` at the head and on the merged tree. Budgets move only down (`class_excess_loc` 18209 to 18202, `max_class_loc` 8449 to 8442), and no `*_budgets.json` raise is involved. `archscore/score.py --diff 5c0ee1093 HEAD`: `Architecture score: dS +0.0000 NULL`. No metric rises, so step 14 has no raise to judge.
- RESULT head (step 7): the body's `## Head` names `274e6975c1b7a4334d181879c4ad2bef532c4134`, the head measured.
- RESULT step 15: the added production lines keep the law inside the pure `thermal_model.reanchor_heat_loss`, and the coordinator only logs and zeroes samples per flag. `coordinator_attrs` is unchanged, and no `config_flow.py` hunk exists. The body raises its reading of the architect note ("re-anchor at the write of the prior" read as the existing anchor-on-load mechanism) as a departure the orchestrator may judge. I find it consistent with `fixer.md` step 17's "the existing mechanism, never a parallel one".
- CI on this head (check-runs API at verdict time):
  - Of 43 runs, 41 concluded success, skipped or neutral, and none is red. Among them: `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / arch-instrument`, `tests / lane-proofs`, `codeql / Analyze (python)`, `arch-score`, `budget-raise-gate`, `governance / policy-docs` and `governance / instrument-self-tests`.
  - `tests / mutation` (job 121031400884): concluded success. Its log was not read, so a green from an evaluated table cannot be told apart from `MUTATION TABLE INCONCLUSIVE`. The answer does not turn on it here: the body's mutants, my own, and all 32 ledger sites were driven above.
  - Two were still open at verdict time: `pr-contract / pr-contract` (queued) and run 40147168912's `prelude` (in progress). So the body check's `record`/`skip red-history` line for the range was not read.
  - The earlier heads' reds are answered in the body's `## Red checks`, with their cheaper detector named or found not to exist: the three STALE PINs and `MUTANTS` window cache at the `eceef457a` merge, and at `3383fb2ac`, `tests / mutation`, `gate` and `pr-contract`.
