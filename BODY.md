This is roster group R10-RATIO-SITES: the two round-10 items the lower-floor learned ratio owns — the seam that omits it, and the published UA whose basis a reader cannot guess.

Closes #2239.

**D-1 (D2-s1-71), the defect.** `_space_demand_kw` summed the two zones' CONFIGURED losses. The model rolls the learned split, so with the ratio off 1 the external-heat detector's standing loss read below the demand the dynamics simulate — 7.741 kW against the model-consistent 11.122 kW at the owner-shaped scale 1.567 / ratio 1.922, 30.4 % low. Its one consumer is the detector's own free-heat estimate, `free_heat_kw = displacement * space_demand_kw`, so the house was promised less free heat than it was getting; the solve and the model never read the value.

The class's rule is the tree's own, on `lower_floor_heat_loss_learned`: *"Every consumer of the dynamics must go through this rather than the raw configured value."* `optimizer.hold_demand_kw`, which prices the tank's drain on the same whole-house quantity, already obeyed it; `_space_demand_kw` was the one that did not. The fix takes the learned term there, and nothing else — `## Figures` enumerates the class and dispositions every seam it returns.

**D-2 residual, label hygiene.** The UA `SysIdResult.as_dict()` publishes is the identified scale carrier on the CONFIGURED zone total the learned scale multiplies — `sysid._zone_heat_loss` times `house_heat_loss_scale`, the base `_candidate_model` divides into that scale and `adoption_decision` divides by. It is NOT the model's effective UA, which also carries the learned lower-floor split. Measured end to end on the stock two-zone house at scale 1.0: the fit publishes 189.9 W/K where the model's effective UA is 244.0 W/K at split 1.6, and the two agree at split 1.0.

**Took "label it".** Publishing the effective figure instead loses on structure, not on taste. That figure already has its own published surface — `house_heat_loss_effective`, which the learning sensor carries as `heat_loss_w_per_k` — so a second copy inside the sysid view duplicates one concept; and `as_dict()` is the fit's own serialization, so a converted number there would no longer be the one `adoption_decision` compares against its base. The label lands at the value's owner (`SysIdResult.heat_loss_kw_per_c`'s field doc) and at the published contract (`SysIdResultView.heat_loss_kw_per_c`), and a check pins the arithmetic the label states, at both ends of the split, so the label cannot outlive a change of basis.

One surface that names the same value is left alone deliberately: the completion log line (`sysid.py:1742`, `UA=%.4f kW/°C`). It prints the fit's own return at the moment the fit finishes rather than a figure a later read compares against the Health tab, and no test pins its text.

## Head

`96bab6f672a6933251190de8d242b51c5769a0c4`: `f5ed45dd7` merges origin/main `e3f3b312f` into the authored head `aa7dac5b4231d86ec725ec8a0686e7af159f9710` with no resolution, and one commit above it re-anchors the carry's cited line to `coordinator.py:10403`. Every figure below was re-taken at this merge base and re-read at this head: both harnesses' arms at both ends, the class enumerations' line anchors, the mutation proof, the gate, `tests/structure.py` and the architecture score. `e3f3b312f` moved only the gate's own files (`tests/entities.py`, `tests/gate_lock.py`, `tests/run.sh`, `tests/derive_closures.sh`, `tools/pr/prepr.sh`) and three policy copies, so nothing the measurements read changed; one figure is a function of the merge base and is stamped where it is quoted.

## Mutation proof

The check was written first. Run against the merge-base production with the branch's `tests/features.py` block, it read `FAIL #2239: the external-heat detector's space demand is the whole-house demand the tank's drain law prices … [got [(False, 1.0, 6.1113, 6.1113), (False, 1.922, 6.1113, 6.1113), (True, 1.0, 7.74098, 7.74098), (True, 1.922, 7.74098, 11.121751)]]` — `1 of 4156 FEATURE CHECKS FAILED`. The two-zone split-1.922 row is the defect; the other three are the controls.

M1 mutates the predicate, not the tail: `params.lower_floor_heat_loss_learned` → `params.lower_floor_heat_loss` in `_space_demand_kw`, `str.replace` under an assertion that the anchor matched exactly once (the same two-line anchor also appears in `_effective_house_heat_loss`, so the replacement carries the `if params.two_zone_enabled:` line to stay unique). Driven at the head: the same check fails with the same four numbers, `1 of 4156 FEATURE CHECKS FAILED`, and nothing else moves.

M0 is the unmutated head: `ALL 4156 FEATURE CHECKS PASSED`.

Both arms ran in the worktree, not in a `git archive` copy. An archive run of the same block reads `1 of 4156` with the single red `and the path that proceeds still stamps a resolvable recorded_at (#363) [recorded_at = 'unknown']` — the #363 artefact fixer.md attributes to the runner, not to this diff, and it is why the arms are taken where git history exists.

## Null control

- The fix's own arms inside the new block: split 1.0 in both the one- and two-zone rows, and the single-zone arm, which does not read the split at all.
- The finder harness's perturbation `--ratio 1.0` reads 0.0000 for that row at BOTH ends, so the baseline's 0.4367 is the split and nothing else.
- The independent harness's `--ratio 1.0` arm reads −0.0000 at both ends.
- Every golden fixture that publishes the split publishes 1.0 (`grep -ho '"lower_floor_loss_ratio": [0-9.]*' tests/golden/*.json | sort | uniq -c` → 5 rows, all 1.0), so the fix is a no-op on the fixture corpus and no golden is claimed or re-recorded.
- The two harnesses' other rows — `sysid_prior_ua_rel_diff`, `sysid_adopt_effective_rel_err` — read flat at both ends: they are the refuted D-2's seams, which this group must not touch (the finder's oracle fed `adoption_decision` a basis the production fit never returns).

## Figures

Finder and catch-up harnesses, each run from the tree with its blob sha1, at the baseline export of `e3f3b312f` and at the head. Commands are the ones printed in each harness's own docstring:

- `PYTHONPATH=tests/hastub python3 tests/features.py`: the block this diff appends; `ALL 4156 FEATURE CHECKS PASSED` at the head, and its #2239 check's failing line carries the figures `30.4 %` is computed from (`7.74098` against `11.121751`).

- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-reseed/reparam_sites.py` (blob `7c49087f39bb`): `space_demand_rel_diff` 0.4367 → 0.0000. The row's own figures: A 7.741 kW → 11.122 kW against a model-consistent 11.122 kW.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-reseed/reparam_sites.py --ratio 1.0`: 0.0000 at both ends (the perturbation).
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/study/ratio_v2.py --scale 1.0 --ratio 1.6` (blob `d185b178b8a2`): its D-1 oracle is the production `ThermalModel`'s own dynamics, not the finder's; `space_demand_vs_dynamics` −0.2213 (4.940 vs 6.344 kW) → +0.0000. Its D-2 arm prints the label's measurement: `fit heat_loss_kw_per_c 189.9 W/K; true effective 244.0 W/K`, flat at both ends.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/study/ratio_v2.py --scale 1.0 --ratio 1.0`: D-1 −0.0000; D-2 `fit 189.9 W/K; true effective 190.0 W/K` — the arm at which the published basis and the effective one coincide.
- The class's seam rule (fixer.md step 8), `grep -rn "lower_floor_heat_loss\b" custom_components/heatpump_optimizer/*.py`, returns six non-definition seams at the merge base and five at the head; the one it loses is `_space_demand_kw`, closed here. The five at the head, each with its disposition:
  - `coordinator.py:4859` `_house_heat_loss_anchor` — already learned (`* self._lower_floor_loss_ratio`).
  - `coordinator.py:5289` the lower-floor learner's own Newton step — takes the CONFIGURED base on purpose: the ratio is the variable it fits. Its control is the harness's own §5 row, `newton_step_ua_ratio_B_over_A=1.0000` at residuals inside the trust region.
  - `sysid.py:159` `_zone_heat_loss` and `sysid.py:1240` `adoption_decision` — the refuted D-2's seams, forwarded as refused by the roster: a recorded refusal, not an open seam.
  - `thermal_model.py:555` — `lower_floor_heat_loss_learned` itself, which owns the rule.
  Four more sum the two zones through the learned term already: `coordinator.py:2535` `_effective_house_heat_loss`, `coordinator.py:4511` `_space_demand_kw` (this diff), `optimizer.py:1899` `hold_demand_kw` and `optimizer.py:4842`.
- The same rule over `grep -rn "heat_loss_coefficient" custom_components/heatpump_optimizer/*.py`, which widens it to every site that builds a house UA from one field: `battery.py:251`/`262` (learned, and its own comment quotes the rule), `optimizer.py:1899`/`4842` and `coordinator.py:2535` (learned), `optimizer.py:2009`, `battery.py:274`, `sysid.py:179`, `coordinator.py:1088` (each the single-zone or upper-zone arm of a branch, correct by construction), `optimizer.py:3184` (a dimensionless weather factor — the coefficient cancels), `sysid.py:338`/`1355` and `coordinator.py:5289` (the fit's own base, self-consistent per the D-2 refutation). One seam is open, and it is not this group's: `coordinator.py:10403`, below.
- `coordinator.py:10403` is the envelope score's loss term, and it is a distinct finding. Command: `PYTHONPATH=tests/hastub python3 -c "import sys;sys.path[:0]=['tests','custom_components'];from dataclasses import replace as R;from harness import FakeEntry,FakeHass;from profiles import house;from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as C,_effective_house_heat_loss as E;from heatpump_optimizer.thermal_model import ThermalParameters as T;cfg=house(two_zone=True,dhw=False);b=R(T.from_config(cfg),heat_loss_coefficient=0.19,house_heat_loss_scale=1.567);c=C(FakeHass(),FakeEntry(data=cfg));[(c.__setattr__('_thermal_params',p),print(lbl,'envelope',c._scores_view()['envelope'],'effective_W_per_K',round(E(p,1.567)*1000,1))) for lbl,p in (('split 1.0',R(b,lower_floor_loss_ratio=1.0)),('split 1.6',R(b,lower_floor_loss_ratio=1.6)),('split 1.6, coefficient x1.5',R(b,lower_floor_loss_ratio=1.6,heat_loss_coefficient=0.285)))]"`, which prints `split 1.0 envelope 17.0 effective_W_per_K 297.7` / `split 1.6 envelope 17.0 effective_W_per_K 382.3` / `split 1.6, coefficient x1.5 envelope 3.0`. The graded time constant is inflated by the split and never sees it; the third arm is the control, that the probe can see movement at all. The plant's `heat_loss_coefficient` is set to the zone total, which is what `presets.py` ships for a two-zone house. It is outside this group's owning seam and R10-SCORES owns the envelope; the measurement and its null arm are carried to that group's brief (see `## Forward-carry`), not fixed here.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir …`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` over 5 changed files. This row is a function of `origin/main`'s tip, so it is stamped: measured at merge base `e3f3b312f`, main's tip then, on 2026-10-17. The rule is the mode line, not the count, and a push to `main` prints no mode line at all.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) bash tests/run.sh`: `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`, and its own scope line reads `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` No red.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `max_class_loc 8635 <= 8635`, unchanged, because the fix is line-neutral in the class; `coordinator_attrs 151` and `seam_cut_total 752` unchanged.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL` — no gate rise, so no metric needs explaining.
- `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `node tools/policy/brief_lint.mjs`: no finding outside its own fixtures.
- `bash tools/pr/prepr.sh <body.md> 2239`: `PRE-PR: 96bab6f672a6933251190de8d242b51c5769a0c4 00000000000000000000000000` — zero refusals; `FIGURES: 12 resolved, 1 not verified, 0 refused`, the unverified one being the inline probe above (`figure_lint` names an inline script rather than a file), and `merge-base e3f3b312fff5`.

## Red checks

`tests/structure.py` — `max_class_loc 8643 > 8635 (+8)` on the branch's first commit. The modifier is that row's zero headroom: the first cut of the fix carried a five-line docstring and a wrapped expression, and `max_class_loc` prices every physical line of the coordinator class, prose included.

The cheaper detector is that same script run locally, whose standing cost is one gate-free run; it is already in the local path (`fixer.md` step 5 requires it before every push, and `tests/structure.py` is a `scope.run` line for any coordinator change), which is how the row was found and paid. The fix is line-neutral in the class — a one-line docstring and a one-line expression — so the head reads 8635. `defect-root-cause.md`'s first trigger does not fire: nothing here reached a release.

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`, group `R10-SCORES`, the appended `carry` entry. Its own carry array asks that "suspected causes" be "measured, not assume[d]" and names "two-zone UA ignored" among them; its brief already requires the envelope grade "use whole-house UA (both zones)" and "once fixed it agrees with the Health tab's figure". What it did not have is the mechanism and the arm that separates it from a scale-only drift, which is what the entry adds — the score's loss term is the configured total, the learned `lower_floor_heat_loss_learned` is absent from it, and the null arm is split 1.0.

Two notes on the destination. The in-tree roster at this merge base is behind the roster branch (`handoff/audit-r10-roster`) in other groups' `resume` and `carry` fields, but `R10-SCORES`' entries are byte-identical in both, so this change merges as an append to one array. And the file is outside this group's declared `files`; it is a brief, which is the destination `finding-propagation.md` names, not a production hunk.

## Friction

- `orchestrator.md: contradiction: the R10-RATIO-SITES roster entry holds two architect notes that disagree -- its `architect_note` names coordinator.py "position 4 of 25; before you: R10-TARIFF, R10-FEEDS" while its `brief` names "position 3 of 24; before you: R10-FAHRENHEIT, R10-FEEDS", and the `after` array names R10-FEEDS alone. The brief was followed; a resumer reading the other field would serialise against a group that finished first.
- `fixer.md`: cost: max_class_loc prices every physical line of the coordinator class, so a docstring or comment line a fix adds to a hot 8.6k-line class costs exactly what code costs, and that row sits at zero headroom. Paying it is why this fix's own explanation is one line.
