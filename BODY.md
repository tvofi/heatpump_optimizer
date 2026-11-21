R11-CARRY-DRAWMAP part A (part 1 of 3): the approved draw-map part A (pass record, map rows beside the running-draw window, the experiment refusal at `MeasuredCop.judge_floor`) ported from archive/handoff/r10-draw-map-evidence-a cc335482ae onto main, per the approved note design/R11-CARRY-DRAWMAP a1688d8d6a (design review approve, design-verdict/R11-CARRY-DRAWMAP 2e7c39a4d9). Part labels are the note's: A = pass record, map rows, learner exclusion; B = the sweep and [CE]; F = the trace and the bundle readers.

Owner gate: rulings S1-S4 (2026-11-14) confirmed standing by the owner's inbox ruling of 2026-11-18 (refs/heads/inbox/r11-carry-drawmap 5daa665b3f, line 1, verbatim "Confirm": "Build part A now per the approved note").

What the port changes against the tag:
- Conflicts resolved against main's metered floor (R11-OUTSIDE-HONEST-METERED-FLOOR) and COP scale probe (R11-OUTSIDE-SELF-SETTING-PUMP): `owed_scale` stays ahead of `judge_floor`; the experiment flag is a keyword after `draw`; `store` keeps main's `draw/engaged` domain and floor leaves, the map-row column leaves added beside them.
- Carry 12: B's typing narrowing of `MapRows.take_pass` (early return on no pass) and `_stored_map` (filtered split), commit 8b4c27bb52, taken; behaviour unchanged (block A passes on it).
- Design verdict note dither-first-cycle: an experiment cycle now reads as no interval for the dither (`MeasuredCop.owed_scale(..., read=False)`), so the step a plan row admitted just before the experiment earned is not taken inside it. Alternatives: (a) skipping `owed_scale` on an experiment cycle leaves the stale admission live for the cycle after, moving the defect one cycle later; (b) adding `COP_REFUSED_OFF_ASK` to the non-read refusals also changes the ratio gate's off-ask verdict (`_judge_ratio` admits the row into the probe before refusing it), a behaviour change outside this group. Taken: the explicit `read` argument, one caller.
- Review block mutation-vacuous (verdict/3737 at 007e7be48d): block A gains "fold commits a closed space run as a row only when the interval is neither frozen nor distorted ...", which drives `draw_range.fold` itself after a closed space run with frozen alone, distorted alone, both, and neither (the control, which commits one row); the earlier check called `MapRows.commit_runs` directly and never read how `fold` wires `keep`.
- Design item 2: the window null gains `floor_kw`, `floor_since` and the solve band (`solve_band(..., applies_floor=True)`), on a run whose learned floor moves.

## Head

7b9204eb3a6e47b2c8f670d940dbd4952eb05007, the code head of this handoff: one commit on 93cbcecb44b14aabcea3ba833fc1daa3620a03ed, which is the PR head 2b95078fafc902468cc6b09a77faddcd6391c85b merged with origin/main 053c33bcc68292b4331986a3c2b538e89fe17e42, the `tests/features.py` conflict resolved as a union. 93cbcecb is the dead local seat's merge 55aca8584739447c82be8b233e56115f86e6db64 re-authored: same tree, same parents, same message. Its author `hpo-seat <hpo-seat@users.noreply.github.com>` was refused by `body_push.sh`'s ref_privacy guard (`unnumbered-email in the author email of 55aca8584739`). The figures measured "at the head 55aca858" hold for 93cbcecb, whose tree is the same. Resolution check: against the merge base b36742b17b7ea229b859fb86a43e74a562bb847b, every line either side adds to `tests/features.py` is present at the head (0 missing from 2b95078f's side, 0 from 053c33bc's), and the line count is the base's plus both sides' additions exactly (97564 + 593 + 212 = 98369). This head merges with origin/main 78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f with no conflict (`git merge-tree --write-tree`). The one commit after the merge deletes main's stale `killed_by` pin `tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_current_hour.RETURN_DEL.a653dd5d.json`. Main's nightly recorded it (464252a8b3) for the coordinator method that this branch moves to a module function. The module function's own pin, `_dhw_current_hour.RETURN_DEL.a2025997`, matches the line at the head (`    return now.hour + now.minute / 60.0`). `prepr.sh`'s ci predict step refused the stale pin at 55aca858: `STALE PIN ... disposition names no site the inventory generates`. The figures from d4e133dc and adf0a38b below were measured before the merge. The figures marked "at the head 55aca858" were measured at the merge. The commit after it changes only the ledger file.

prepr: passed rc=0 at 7b9204eb3a6e47b2c8f670d940dbd4952eb05007 (`PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`, scoped, `PRE-PR: ... rc=0`). After the main merge: `tests/features.py` (`ALL 5975 FEATURE CHECKS PASSED`) and `tests/structure.py` (rc=0) re-run at 55aca858; prepr's `merged structure` step passed on this head merged with origin/main. CI is the authority for the rest of the scoped set.

## Mutation proof

- `coordinator._fold_measured_cop`: `owed_scale(..., not experiment)` replaced by `owed_scale(..., True)`; block A (`features_block.py --prelude "exec(open('<prelude>').read())" 'R.section("R10-DRAW-MAP-EVIDENCE part A: map rows and the learner exclusion")'`, prelude by `--emit-prelude`): `FAIL the dither's first experiment cycle: a run whose cycle 55 is an experiment, entered with the row before it admitted, takes no dither step inside it ...`; 1 of 33 failed. Restored: 33 of 33 pass.
- The tag's own A block, at main's production code with this head's `tests/features.py`: the block stops at its import (`AttributeError: module 'heatpump_optimizer.draw_range' has no attribute 'PassRecord'`); at the head 33 of 33 pass.
- `draw_range.fold`'s `draw.map.commit_runs(keep=not (frozen or distorted))`, the review's mutants driven by its own `mutant_driver.py` (verdict/3737 ev/) on block A at the head:
  - `keep=True`: `FAIL fold commits a closed space run as a row only when the interval is neither frozen nor distorted ...`; 1 of 33 failed.
  - `keep=not distorted` (frozen ignored): the same check fails; 1 of 33.
  - `keep=not frozen` (distorted ignored): the same check fails; 1 of 33.
  - `keep=False`: that check and the window null's "rows were kept" fail; 2 of 33.
  - Restored: 33 of 33 pass.
- At the head 55aca858, the review's three mutants of `draw_range.fold`'s `draw.map.commit_runs(keep=not (frozen or distorted))`, each written into its own `git archive HEAD` copy and run with `PYTHONPATH=tests/hastub python3 tests/features.py`:
  - `keep=True`: `2 of 5975 FEATURE CHECKS FAILED`. Killed by `FAIL fold commits a closed space run as a row only when the interval is neither frozen nor distorted ...`.
  - `keep=not distorted`: `2 of 5975`. Killed by the same check.
  - `keep=not frozen`: `2 of 5975`. Killed by the same check.
  - The second FAIL in each run is `and the path that proceeds still stamps a resolvable recorded_at (#363)  [recorded_at = 'unknown']`. It comes from the copy, which has no git metadata, and not from the mutant (`tools/audit/seat/mutant_run.py`'s docstring: the #363 check fails in a copy on every mutant, baseline included). Null: the unmutated copy reads `1 of 5975 FEATURE CHECKS FAILED`, and that one FAIL is the #363 check.
  - Head, in place: `ALL 5975 FEATURE CHECKS PASSED`.
- `pump_arbiter._flow_target`'s `lo=min(m.floor_c, m.heat_c),` -> `lo=(m.floor_c),` (the CLAMP_DROP that `tests / mutation` and `mutation-autofix` left alive at 212e7976): `PYTHONPATH=tests/hastub python3 tests/features.py` with the mutant in place: `FAIL the heating floor is capped by the ceiling before the entity's minimum decides ...`, the only FAIL among 5540 checks; restored, 5540 ok and 0 FAIL. Both runs were stopped at 1500 s by `timeout`, and both had passed the block. CI's `tests / fast` runs the whole script.
- The mutation draw over the diff's added lines is CI's `tests / mutation`.

## Null control

- Window null (block A, "null: DrawRange.samples, engaged, ask_evidence, the floor, the learned floor and its count, the solve band's bottom and the stored window ..."): the same 240 intervals folded with and without map rows leave every window reader identical; the check also asserts its precondition, a learned floor set and the band's bottom not `configured` in the run without rows, so the extension is not vacuous (on the 80-interval fixture the tag used, the floor never moved: `floor None`).
- Dither null (block A, "the dither's first experiment cycle"): precondition asserted, the row before cycle 55 admitted (the probe arms at cycle 47 on this run); from cycle 56 to the end the trace equals the run with cycle 55 frozen; control arm, the same cycle under the plan steps the scale off the probe's base.
- COP exclusion null (tag's check, unchanged): an experiment interval leaves the learner state byte-identical to the same interval frozen and to the run without it.

## Figures

- Block A at the head: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" 'R.section("R10-DRAW-MAP-EVIDENCE part A: map rows and the learner exclusion")'` -> `ALL 33 FEATURES BLOCK PASSED`.
- Harness `dev/audit/harnesses/draw_map_rows.py` (sha1 057455db8d886d3b112e0c43a2b422d3de37e220), `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/draw_map_rows.py --synthetic`: head `RESULT store rows=672 draw_record_bytes_empty=83 draw_record_bytes_capped=58141 added_bytes=58058`, `RESULT open_loop rows=25 distinct_c=18 gain_kw_per_k=0.300 offset_kw=0.400 planted_gain=0.3 planted_offset=0.4`, null `RESULT shuffled ... gain_kw_per_k=0.023`; at main's code the harness stops (`AttributeError: 'DrawRange' object has no attribute 'map'`).
- Typing: `cd custom_components && mypy --strict --ignore-missing-imports heatpump_optimizer/draw_range.py`: before the carry-12 narrowing 5 errors in `draw_range.py` (`take_pass` x4, `_stored_map` x1); after, none in `draw_range.py`. Local mypy is not CI's pinned pair; `tests / typing` is the authority.
- Ratchet: `python3 tests/structure.py` reported one gain, `seam_cut_total` (the hot-water clock `_dhw_current_hour` left the coordinator class as a module function), recorded with `--record`; re-run clean.
- Triage deleted with the tag: `tests/mutation_ledger/survivor_triage/pump_arbiter.py/_flow_target.CLAMP_DROP.38a077e7.json`; its `old` text `lo=min(floor_c, heat_c),` occurs once in main's `pump_arbiter.py` and zero times at the head (`grep -cF`). Its `equivalent` verdict did not hold. When the entity's minimum is above the configured ceiling, `SetpointGrid.bounded` drops the ceiling, so the mutant's `lo` becomes the floor. In the new features check, a 30 degC ceiling with a 35 degC minimum and a 40 degC tank writes 35.0 at all three levels (1.5, 3.5 and 5.5 kW) at the head, and 45.0 under the mutant (scratch probe, head against mutant). Null: a 20 degC minimum writes 30.0 and a 50 degC ceiling writes 50.0, under both texts. The site is now killed by that check, not triaged.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` -> MODE line below; every script in `scope.run` run locally with `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`: 28 of 28 exit 0.
- Sibling seams (`fixer.md` step 8), rule `git grep -n "judge_floor(" -- custom_components`: `coordinator._fold_measured_cop` (closed here, experiment flag); the heat-counter span close in `coordinator.py` (`_async_learn_heat_span`'s caller passes `close.refusal` first, which carries the cycle's `draw_off_ask`: already guarded, tag check "a heat counter span holding an experiment cycle folds no COP" passes). Rule `git grep -n "owed_scale(" -- custom_components`: `MeasuredCop.owed_scale` (closed here), its one caller (closed here).

<!-- figure-block: scope-line mb=053c33bcc68292b4331986a3c2b538e89fe17e42 head=7b9204eb3a6e47b2c8f670d940dbd4952eb05007 -->
~~~text
MODE: SCOPED -- 28 script(s) run, 5 scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

Every site `tools/pr/ci_predict.py` lists as added and unpinned at this head, each killed or pinned by the `mutation-autofix` lane after the push (all under `custom_components/`, the lane's scope):

- `custom_components/heatpump_optimizer/accuracy.py:1241 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/accuracy.py:1278 BOOLOP`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:5352 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/coordinator.py:5354 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:120 CONST`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:122 CONST`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:124 CONST`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:126 CONST`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:167 RETURN_DEL`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:182 CMP_BOUND`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:183 CMP_BOUND`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:183 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:197 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:199 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:201 RETURN_DEL`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:222 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:228 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:231 CMP_BOUND`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:234 CMP_BOUND`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:236 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:238 BOOLOP`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:238 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:245 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:264 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:266 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:273 RETURN_DEL`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:280 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:282 BOOLOP`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:282 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:285 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:287 RETURN_DEL`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/draw_range.py:292 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:972 CLAMP_DROP`: survived the autofix lane at 212e7976. It is killed by the `tests/features.py` check "the heating floor is capped by the ceiling before the entity's minimum decides" (see Mutation proof), and mutation-autofix pinned it at 247ce3b6 (`tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_target.CLAMP_DROP.6dfae9cd.json`).
- `custom_components/heatpump_optimizer/pump_arbiter.py:1012 RETURN_DEL`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1369 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1371 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1373 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1375 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1377 CMP_BOUND`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1378 RETURN_DEL`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1391 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)

## Architecture score

- `coord_footprint` 2507 -> 2508: the one statement the experiment exclusion needs in the coordinator class, `experiment = self._current_action.get("mode") == "system_identification"` in `_fold_measured_cop`, which reads the cycle's own action (the coordinator's state) once and hands the flag to both `MeasuredCop.owed_scale` and `MeasuredCop.judge_floor`; the hot-water clock `_dhw_current_hour` leaving the class pays part of the port's statements. Alternative not taken: passing the whole action into `accuracy.MeasuredCop` would move a coordinator concept (the action's mode key) into the learner module. Command: `python3 tools/audit/archscore/score.py --diff 9fe63d00b59f100aea67267ddddc95522e164aa1` -> `Architecture score: dS -0.0006 WORSENS (inadmissible: coord_footprint 2507->2508)`.

## Red checks

- `tests / mutation` at adf0a38ba134 (red at 007e7be48d0f): red by construction on the 41 sites under `## Unpinned sites` (lines this diff adds, none yet in the ledger); `mutation-autofix` pins the killed sites after the push. Cheaper detector: `tools/pr/ci_predict.py`, which predicted it here offline in about a minute; it already runs in `prepr.sh`, so no countermeasure is owed.
- `arch-score / arch-score` at 007e7be48d0f: `FAIL: dS -0.0006 WORSENS; unexplained: coord_footprint 2507->2508` because the body had no `## Architecture score` section; answered by the section above. Cheaper detector: `tools/audit/archscore/score.py --diff <merge base>`, offline in under a minute, which `prepr.sh` does not run (its `ci predict` step predicted no red here); no countermeasure is built in this group, whose seam is the draw map, not the pre-PR instruments.

- `tests / mutation` and `gate` at 212e7976 (job 135087753389; gate job 135152747325 `FAIL tests / mutation`), with `mutation-autofix` (job 135113511239, `skip-nothing-killed`): `ADDED UNPINNED custom_components/heatpump_optimizer/pump_arbiter.py:972 CLAMP_DROP`, which no driver killed. Cause: the deleted triage's equivalence claim was wrong (see Figures), and no check covered an entity minimum above the ceiling. Fixed by the new features check. Cheaper detector: `tools/pr/ci_predict.py` lists the site as unpinned, but it cannot tell whether autofix will kill it. Only a local `mutation_table.py --anchor` drive would have told. No countermeasure is built here.

- `governance / wave-script` at 2b95078f (job 136821027746): `295 passed, 1 failed`, `FAIL ownerOnlyRecord reads every declared owner-only brief's id, seat and dimension, and no near-miss []`. Cause: a skew between the check source and the tree. The run was a branch push, so the job restored its check source from `PINNED: origin/main`, then main 9e7abae6bbce9bc971393a5010ae099dfd9e6a90. That source reads the owner-only brief `dev/governance/dimensions/DX0.md`, which main carried but the 2b95078f tree did not. Main itself was not red: main's own checker on main's own tree reads `296 passed, 0 failed`. Reproduction: 9e7abae6's pinned check source (145 paths, 7 differ) restored onto the 2b95078f tree reads `295 passed, 1 failed` with the same FAIL line. Repair: the main merge at this head brings DX0.md in. `node .claude/workflows/check-wave-script.mjs` at the head reads `296 passed, 0 failed`. This diff touches no wave-script or owner-only file. Cheaper detector: `git merge-tree --write-tree origin/main HEAD`, which `prepr.sh` already runs. Its tree conflict made the PR DIRTY, and the merge that cures that conflict also cures this red. No countermeasure is owed.
- `tests / fast (3.14)` at d726d08e12 (job 135570141109, 2026-11-19), a merge of main cb8edb65a5a9c0940dbe263acee49e02ba5f0b25 into this branch: `1 of 5967 FEATURE CHECKS FAILED`, `FAIL the lift may raise the plan's peak over the unlifted plan's ...`. This red is inherited from main: cb8edb65's own `tests / fast (3.14)` (job 135486106404) fails on the same check, `1 of 5933`. The check comes from R11-CARRY-ROOM-LIFT (338aa528f9), outside this seam. It compared solver trajectories bit for bit, which fails under OpenBLAS's SkylakeX kernel. Main repaired it in 890a05e9cf ("compare the lift-peak plans within 1e-3 K"), which this head contains. Later heads of this PR pass it (2b95078f, job 136821026935), and so does this head locally (`ALL 5975 FEATURE CHECKS PASSED`).
- `pr-contract / pr-contract` at 2b95078f (job 136667994523): `check governance / wave-script is red and ## Red checks does not name it`. Answered by the entry above.
- `codeql / Analyze (python)` and `governance / env-matrix` at 2b95078f concluded cancelled. Not a repair: this push re-runs them.

## Forward-carry

- Carry 0 (D15 scope of the debug week and bundle): part F's, built with its debug week. Carry: R11-CARRY-DRAWMAP
- Carry 1 (empty ceiling store; probe before fit): part B's [CE] 2 under S3; `draw_map_linearity.py --bundle` needs the owner's bundle, not in the tree: unmeasured here. Carry: R11-CARRY-DRAWMAP
- Carry 2 (rulings S1-S4): confirmed by the owner 2026-11-18 (inbox line 1); B builds S1 and S3, F builds S2 and S4. Carry: R11-CARRY-DRAWMAP
- Carry 3 (sweep kind to a sweep origin in `pump_arbiter.pass_origin`): part B's; this part's origin check pins the probe and fit kinds. Carry: R11-CARRY-DRAWMAP
- Carry 4 (run key holds the level kW; the sweep routing invariant in `draw_range.fold`): part B's; the null mutant goes on the sweep exclusion B adds to `fold` (verdict note null-mutant-site). Carry: R11-CARRY-DRAWMAP

## Friction

none
