R11-CARRY-DRAWMAP part A (part 1 of 3): the approved draw-map part A (pass record, map rows beside the running-draw window, the experiment refusal at `MeasuredCop.judge_floor`) ported from archive/handoff/r10-draw-map-evidence-a cc335482ae onto main, per the approved note design/R11-CARRY-DRAWMAP a1688d8d6a (design review approve, design-verdict/R11-CARRY-DRAWMAP 2e7c39a4d9). Part labels are the note's: A = pass record, map rows, learner exclusion; B = the sweep and [CE]; F = the trace and the bundle readers.

Owner gate: rulings S1-S4 (2026-11-14) confirmed standing by the owner's inbox ruling of 2026-11-18 (refs/heads/inbox/r11-carry-drawmap 5daa665b3f, line 1, verbatim "Confirm": "Build part A now per the approved note").

What the port changes against the tag:
- Conflicts resolved against main's metered floor (R11-OUTSIDE-HONEST-METERED-FLOOR) and COP scale probe (R11-OUTSIDE-SELF-SETTING-PUMP): `owed_scale` stays ahead of `judge_floor`; the experiment flag is a keyword after `draw`; `store` keeps main's `draw/engaged` domain and floor leaves, the map-row column leaves added beside them.
- Carry 12: B's typing narrowing of `MapRows.take_pass` (early return on no pass) and `_stored_map` (filtered split), commit 8b4c27bb52, taken; behaviour unchanged (block A passes on it).
- Design verdict note dither-first-cycle: an experiment cycle now reads as no interval for the dither (`MeasuredCop.owed_scale(..., read=False)`), so the step a plan row admitted just before the experiment earned is not taken inside it. Alternatives: (a) skipping `owed_scale` on an experiment cycle leaves the stale admission live for the cycle after, moving the defect one cycle later; (b) adding `COP_REFUSED_OFF_ASK` to the non-read refusals also changes the ratio gate's off-ask verdict (`_judge_ratio` admits the row into the probe before refusing it), a behaviour change outside this group. Taken: the explicit `read` argument, one caller.
- Design item 2: the window null gains `floor_kw`, `floor_since` and the solve band (`solve_band(..., applies_floor=True)`), on a run whose learned floor moves.

## Head

58b59591aacc80b6cb5cdbdf34d8b255ceb98b58, measured on merge base ae0ed64af898d8923ac35afe6e9c031ac1e6b111 (2026-11-18T14:58Z).

## Mutation proof

- `coordinator._fold_measured_cop`: `owed_scale(..., not experiment)` replaced by `owed_scale(..., True)`; block A (`features_block.py --prelude "exec(open('<prelude>').read())" 'R.section("R10-DRAW-MAP-EVIDENCE part A: map rows and the learner exclusion")'`, prelude by `--emit-prelude`): `FAIL the dither's first experiment cycle: a run whose cycle 55 is an experiment, entered with the row before it admitted, takes no dither step inside it ...`; 1 of 32 failed. Restored: 32 of 32 pass.
- The tag's own A block, at main's production code with this head's `tests/features.py`: the block stops at its import (`AttributeError: module 'heatpump_optimizer.draw_range' has no attribute 'PassRecord'`); at the head 32 of 32 pass.
- The mutation draw over the diff's added lines is CI's `tests / mutation`.

## Null control

- Window null (block A, "null: DrawRange.samples, engaged, ask_evidence, the floor, the learned floor and its count, the solve band's bottom and the stored window ..."): the same 240 intervals folded with and without map rows leave every window reader identical; the check also asserts its precondition, a learned floor set and the band's bottom not `configured` in the run without rows, so the extension is not vacuous (on the 80-interval fixture the tag used, the floor never moved: `floor None`).
- Dither null (block A, "the dither's first experiment cycle"): precondition asserted, the row before cycle 55 admitted (the probe arms at cycle 47 on this run); from cycle 56 to the end the trace equals the run with cycle 55 frozen; control arm, the same cycle under the plan steps the scale off the probe's base.
- COP exclusion null (tag's check, unchanged): an experiment interval leaves the learner state byte-identical to the same interval frozen and to the run without it.

## Figures

- Block A at the head: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" 'R.section("R10-DRAW-MAP-EVIDENCE part A: map rows and the learner exclusion")'` -> `ALL 32 FEATURES BLOCK PASSED`.
- Harness `dev/audit/harnesses/draw_map_rows.py` (sha1 057455db8d886d3b112e0c43a2b422d3de37e220), `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/draw_map_rows.py --synthetic`: head `RESULT store rows=672 draw_record_bytes_empty=83 draw_record_bytes_capped=58141 added_bytes=58058`, `RESULT open_loop rows=25 distinct_c=18 gain_kw_per_k=0.300 offset_kw=0.400 planted_gain=0.3 planted_offset=0.4`, null `RESULT shuffled ... gain_kw_per_k=0.023`; at main's code the harness stops (`AttributeError: 'DrawRange' object has no attribute 'map'`).
- Typing: `cd custom_components && mypy --strict --ignore-missing-imports heatpump_optimizer/draw_range.py`: before the carry-12 narrowing 5 errors in `draw_range.py` (`take_pass` x4, `_stored_map` x1); after, none in `draw_range.py`. Local mypy is not CI's pinned pair; `tests / typing` is the authority.
- Ratchet: `python3 tests/structure.py` reported one gain, `seam_cut_total` (the hot-water clock `_dhw_current_hour` left the coordinator class as a module function), recorded with `--record`; re-run clean.
- Triage deleted with the tag: `tests/mutation_ledger/survivor_triage/pump_arbiter.py/_flow_target.CLAMP_DROP.38a077e7.json`; its `old` text `lo=min(floor_c, heat_c),` occurs once in main's `pump_arbiter.py` and zero times at the head (`grep -cF`).
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` -> MODE line below; every script in `scope.run` run locally with `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`: 28 of 28 exit 0.
- Sibling seams (`fixer.md` step 8), rule `git grep -n "judge_floor(" -- custom_components`: `coordinator._fold_measured_cop` (closed here, experiment flag); the heat-counter span close in `coordinator.py` (`_async_learn_heat_span`'s caller passes `close.refusal` first, which carries the cycle's `draw_off_ask`: already guarded, tag check "a heat counter span holding an experiment cycle folds no COP" passes). Rule `git grep -n "owed_scale(" -- custom_components`: `MeasuredCop.owed_scale` (closed here), its one caller (closed here).

<!-- figure-block: scope-line mb=ae0ed64af898d8923ac35afe6e9c031ac1e6b111 head=58b59591aacc80b6cb5cdbdf34d8b255ceb98b58 -->
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
- `custom_components/heatpump_optimizer/pump_arbiter.py:972 CLAMP_DROP`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1012 RETURN_DEL`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1369 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1371 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1373 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1375 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1377 CMP_BOUND`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1378 RETURN_DEL`: pinned by mutation-autofix (lane mutates custom_components/)
- `custom_components/heatpump_optimizer/pump_arbiter.py:1391 GUARD_OFF`: pinned by mutation-autofix (lane mutates custom_components/)

## Red checks

- `mutation` at 58b59591aacc: red by construction on the 41 sites under `## Unpinned sites` (lines this diff adds, none yet in the ledger); `mutation-autofix` pins the killed sites after the push. Cheaper detector: `tools/pr/ci_predict.py`, which predicted it here offline in about a minute; it already runs in `prepr.sh`, so no countermeasure is owed.

## Forward-carry

- Carry 0 (D15 scope of the debug week and bundle): part F's, built with its debug week. Carry: R11-CARRY-DRAWMAP
- Carry 1 (empty ceiling store; probe before fit): part B's [CE] 2 under S3; `draw_map_linearity.py --bundle` needs the owner's bundle, not in the tree: unmeasured here. Carry: R11-CARRY-DRAWMAP
- Carry 2 (rulings S1-S4): confirmed by the owner 2026-11-18 (inbox line 1); B builds S1 and S3, F builds S2 and S4. Carry: R11-CARRY-DRAWMAP
- Carry 3 (sweep kind to a sweep origin in `pump_arbiter.pass_origin`): part B's; this part's origin check pins the probe and fit kinds. Carry: R11-CARRY-DRAWMAP
- Carry 4 (run key holds the level kW; the sweep routing invariant in `draw_range.fold`): part B's; the null mutant goes on the sweep exclusion B adds to `fold` (verdict note null-mutant-site). Carry: R11-CARRY-DRAWMAP

## Friction

none
