R10-WHY-NOW-WIDGET (tvofi 2026-11-01, rulings card 2 option (c) part (b)): a live "Why now" block for the current slot, built to the approved note at design/R10-WHY-NOW-WIDGET 60d61fcf (verdict 043b31ad). The solver publishes five signed drivers per step (`price_rank`, `comfort_floor`, `mold_guard`, `away`, `forecast`). Each is a percent of that step's push, and the magnitudes sum to 100. `get_current_action` carries step i's drivers through `slot_drivers.why_now_at`, at the one index it already finds. The space-plan sensor publishes them as `why_now`, and the card renders them after the headline narrative, in en and sv, with the metric in plain words as every hover.

**Owning seam.** A new pure module, `custom_components/heatpump_optimizer/slot_drivers.py` (numpy, no Home Assistant import). `_build_result` calls `slot_drivers.space_drivers` once. The away setback enters as a solver input, `SolveLimits.away_floor_drop_c`, from `away.floor_drop_c`, which shares `_setback_target` with `solve_bands`, so the setback's condition is written once. `_build_comfort_bounds` returns a fourth element, (the comfort floor before the mold guard, the padded mold floor), which `_Horizon` carries to the drivers.

**Coordinator growth (r3-b), the whole of it.**
- `_solve_record` passes one kwarg (`away_floor_drop_c=`).
- The module-level `_apply_result_payload` copies `why_now` when the action carries one.
- `HeatPumpOptimizerCoordinator` gains no method body and no attribute, so there is no seam_map entry. The what-if solve is untouched.

**Departures from the note, each raised here.**
- `_Horizon` carries a third field, `away_floor_drops`, beside `comfort_floors` and `mold_floors`. `_build_result` sees only the horizon, and `_Horizon` is the per-solve carrier by its own docstring.
- `slot_drivers.step_reasons` owns step i's `space_reason` and `dhw_reason` reads as well as `why_now`.
- The attribute comes from a `SpaceHeatingPlanSensor.extra_state_attributes` override, not from inside `_PlanSensorBase`'s 150-line method.
- No `coord_*` claim: the coord captures never solve, so no why_now key can reach them.
- The card's tile and Plan-page figures under docs/img/card were re-taken after card_browser.mjs's P40 refused them.
- `knownCodes` is the one unknown-code filter shared by the score and the why-now block.
- The card shows each weight as a whole signed percent.

**Brief carries.**
- Carry 1, the group's spec from the owner's 2026-11-01 ruling, is implemented whole. Its strings are verbatim in en and sv, except the two sentences of the metric explanation round 5 rewords (finding 1).
- Carry 2 and Carry 3 (PR 3198 item 7c609975, the same P9 defect recorded twice) are the clip-walk fix: `unreachable()` in tests/card_browser.mjs starts its walk at `run.el`, so it reports a run clipped by its own box.

**This pass (repair round 6: the closures red at 4f8ab9654).**
- **The red.** The previous pass made tests/features.py import `dev/audit/harnesses/r10_demand_overbook.py` to drive `comfort_schedule`. That file sat on the `dev/audit/harnesses/` INERT prefix, so `tests / closures` (job 128558742815) read INERT READS UNDER-APPROXIMATED on features.py, and `tests / closures-autofix` (job 128558743106) ended skip-merge-failed. The recorder cannot file a file that a script imports in-process under `inert_reads` alone, and the merge refuses a file that is both INERT and recorded.
- **The fix (e51073c67).** The harness joins `INERT_EXCEPT` in tests/closure.py, with a comment naming the read and the job, the way `record_burst_replay.py` did. Then `./tests/derive_closures.sh --single tests/features.py` adds it to features.py's closure. So an edit to the harness now selects tests/features.py, which pins it. Two alternatives lost. Filing the read under `inert_reads` would leave the harness INERT while features.py reads it, which is the pair the merge refuses. Dropping the import from features.py would undo the previous pass's class fix: a stale caller would again raise only in a lane nobody runs.
- **Its consequence (69f76c2b3).** With the harness off the prefix, `tests/harness_headers.py`'s read of it had to be in that closure too. prepr.sh step 6d predicted UNDER-SCOPED on `tests / closures`, and the prepr self-test's `pleftrec` null control failed on the same entry. `./tests/derive_closures.sh --single tests/harness_headers.py` files it, beside the `inert_reads` entry that record_burst_replay.py also keeps.
- No production line changes in this pass.

**Round 5 (repair for fix review blocked 97786d25), carried unchanged.** The class fix: every caller of `_build_comfort_bounds` reads the 4-tuple, and the harness caller reads through `comfort_schedule`. Finding 1: the metric text is reworded, not gated. Finding 2: `why_now` is in `_PlanSensorBase._unrecorded_attributes`. Finding 3: mutants C, D and E each have a killing check. One new check kills four diff-mutant survivors. Its mutation proofs are below. Its figures were measured at 9cde30560 and 0765b49d9, and each is labelled with its SHA.

## Head

`dbf79f836ea9acf89f3a076a94fa5c45962e2e88` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

69f76c2b365cd3e2cc306bb1a18f99c306a64d89, merge base 8a1358e8448e6734ed16982f25da6aae223ba8b9.
- 4f8ab9654 is the relay's merge of origin/main into the round-5 tip 0765b49d9. This pass adds two commits above it, e51073c67 and 69f76c2b3. `git diff --name-only 4f8ab9654 69f76c2b3` is tests/closure.py and tests/closures.json.
- At 2026-11-08T00:10Z, origin/main was 17e1157925908bd69addb58ed824c1ac22bfa82f. `git merge-tree --write-tree origin/main HEAD` returns rc 0 with no conflict. Per the owner ruling of 2026-11-07, main was not merged.
- Re-taken in this pass: the closure checks, tests/features.py under the recorder, tests/entities.py, the card checks, the harness `--dp` run, the diff-mutant run, structure.py, the archscore run and prepr.sh. The scoped gate is `MODE: FULL` at this head (see Figures), so the full suite is CI's to run.

## Mutation proof

- This pass's fix. Remove the `INERT_EXCEPT` entry, which is the tree at 4f8ab9654. `python3 tests/closure.py check --in-dir $REC --partial` then exits rc 1 ("1 closure(s) are stale. Re-derive the named script"). At 69f76c2b3 the same recording reads rc 0. `$REC` is `./tests/derive_closures.sh --single tests/features.py --record-only --out-dir $REC`, recorded at e51073c67.
- Its consequence. At e51073c67, without 69f76c2b3's closure line, prepr.sh step 6d printed `PREDICT tests / closures UNDER-SCOPED tests/harness_headers.py: dev/audit/harnesses/r10_demand_overbook.py leaves INERT in this diff`. At 69f76c2b3, `tools/pr/ci_predict.py --base 8a1358e8448e` reads `no closures, fast, governance or instrument red predicted`.
- Round 5's proofs stand, because this pass changes no line they mutate:
  - The class: a 3-tuple unpack at the harness site or the production site raises `ValueError('too many values to unpack (expected 3, got 4)')`.
  - C: FAIL "at every step the rows run largest magnitude first, an idle push ahead of a smaller run push".
  - D: FAIL "_solve_record hands the solve away.floor_drop_c while away, None at home".
  - E: FAIL "the drivers' comfort floor is the margined floor, below the mold floor's raise".
  - slot_drivers.py :84, :96, :118 and :143: FAIL "the forecast window floors at one step and clips at -1; comfort clips at -1; step_reasons past the end is None".
  - Finding 1: the card checks FAIL "why-now: every en string has its sv twin, and every driver code has a label and an explanation".
  - Finding 2: `why_now` is absent from `_unrecorded_attributes` without the sensor line.
  - sensor.py:1637 RETURN_DEL: tests/entities.py exits rc 1 with `AttributeError: 'NoneType' object has no attribute 'get'`.
  - The earlier passes' M1–M14, C1–C9 and the 14 `--pin-killed` sites.

## Null control

- The closure check at 4f8ab9654 against the same recording exits rc 1, and at 69f76c2b3 rc 0. So the check reads the defect.
- `--single tests/features.py` reports `would drop 1 file(s) the committed closure listed; keeping them` (tests/replay/owner-2026-10-30-away.json). The `--partial` merge keeps it, so the closure only grew, by the one harness line.
- The harness `--dp` run prints the same `dp_learned.gap -0.0006` and `dp_true.gap -0.0012` at 69f76c2b3 as at 9cde30560 and 53273de4.
- tests/entities.py fails the same 3 workflow probes it fails at the round-5 base 53273de4: the coverage job's cache key, the release ZIP and the Pages workflow. The diff touches no file they read.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` at e51073c67 printed `MODE: FULL -- every test script runs, nothing is scoped out.` with the reason `tests/closure.py changes the gate itself, so every closure is suspect`. That is a gate-file diff, not CI to reproduce (fixer.md step 5).
- Closure check: `python3 tests/closure.py check --in-dir $REC --partial` at 69f76c2b3 printed `closure: committed closures cover every file this run touched`, rc 0.
- `./tests/derive_closures.sh --single tests/features.py` at e51073c67: exit 0. The recorded run's output reads `ALL 4937 FEATURE CHECKS PASSED`.
- `./tests/derive_closures.sh --single tests/harness_headers.py` at 69f76c2b3: exit 0, `tests/harness_headers.py 404 files`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at e51073c67: `3 of 2657 ENTITY CHECKS FAILED`, the 3 workflow probes under Null control.
- `PYTHONPATH=tests/hastub:tests python3 dev/audit/harnesses/r10_demand_overbook.py --one owner_i01 dp` at 69f76c2b3: rc 0, `dp_learned.gap -0.0006`, `dp_true.gap -0.0012`.
- `node tests/card.mjs` (after `tests/plan_view.py`) at 69f76c2b3: ALL CARD CHECKS PASSED. `node tests/card_drift.mjs origin/main`: `card_drift: 1 state(s) moved and claimed, 44 identical`.
- Diff mutants: `python3 -I tools/audit/seat/mutant_run.py --diff 8a1358e8448e...HEAD --cmd "<MUTANT_CMD>" --max-mutants 66 --report-only` at 69f76c2b3 ran all 66 mutants. The count is `--list`'s `MUTANT` lines. Wall time was 586 s. There were 3 survivors:
  - sensor.py:1637 RETURN_DEL: killed by tests/entities.py, which is outside the block (Mutation proof).
  - slot_drivers.py:23 GUARD_OFF: equivalent, because the guarded imports are type-only under `from __future__ import annotations`.
  - slot_drivers.py:136 CMP_BOUND: equivalent, triaged at `tests/mutation_ledger/survivor_triage/slot_drivers.py/_direction.CMP_BOUND.23463a3d.json`.
  - `MUTANT_CMD` is `env PYTHONPATH=tests/hastub:tests python3 tools/audit/seat/features_block.py --prelude 'from types import SimpleNamespace' --prelude 'from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState' '# --- R10-WHY-NOW-WIDGET: per-slot drivers' '# R10-CLONE-2238 (#2238'`. prepr.sh step 6d' at e51073c67 printed the same 3 survivors.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Claim files: three-dot `git diff 8a1358e8...HEAD -- tests/golden/claimed_drift.txt` is empty. card_claimed_drift.txt carries only this branch's `score_open` entry, under `claims-for:` equal to VERSION. VERSION, the manifest version and RELEASE_NOTES.md are untouched.
- Round 5, at 9cde30560 / 0765b49d9 (carried):
  - The class census, `git grep -n '_build_comfort_bounds(' -- custom_components tools tests dev ':!*.tsv'`, returned 12 lines. Each is dispositioned in round 5's body: one def, one production caller, one harness caller, five older and four new features.py lines.
  - The harness rc census returned 65 scripts, each with the same rc at head and base.
  - The why-now block alone: ALL 25 FEATURES BLOCK PASSED.
- `bash tools/pr/prepr.sh <this body>` at 69f76c2b3, with MUTANT_CMD as above and MUTANT_MAX=66: `PRE-PR: 69f76c2b365cd3e2cc306bb1a18f99c306a64d89 … rc=0`. It printed `CI PREDICT: no closures, fast, governance or instrument red predicted against 8a1358e8448e` and `ancestry reds: the body answers every red this branch pushed`. The code-scanning alert read was skipped (`HTTP 403`), as the step prints. The run was clean at the first head where it ran clean. Per the owner ruling, main was neither merged nor re-run against.

## Unpinned sites

none. This pass adds no production line. The added lines are an `INERT_EXCEPT` tuple entry with its comment, and two closure-table lines. The round-5 diff-mutant survivors are dispositioned under Figures.

## Red checks

These are the concluded reds of 4f8ab9654, on the single check-run page, total_count 68:
- `tests / closures`, job 128558742815 (run 42419763628): `INERT READS UNDER-APPROXIMATED ... tests/features.py: dev/audit/harnesses/r10_demand_overbook.py`. Class: a real closure defect of this branch, repaired in e51073c67 and 69f76c2b3. Cheaper detector: one exists, and it is already in the tree. `./tests/derive_closures.sh --single tests/features.py`, or `PREPR_RECORD_CLOSURES=1`, records the read in about 10 minutes, and its merge names the INERT pair. Round 5 ran prepr.sh step 6b without recording, and step 6d's static predictor does not follow an in-process import from a test script into an INERT harness, so it predicted nothing. The standing cost is the ~600 s recording, owed whenever a test script gains an import, so the answer is to run it. This pass did.
- `tests / closures-autofix`, job 128558743106: `digest-mismatch: error`, `AUTOFIX: skip-merge-failed`. Class: the same defect. The autofix merge refuses the INERT-and-recorded pair, so no bot repair could land. Cheaper detector: the same as the bullet above.
- `pr-contract / pr-contract`, job 128558743233 (run 42419763628) and job 128558143070 (run 42420070733): `PR-BODY: 2 error(s)`, because `## Red checks` did not name the two closures reds. Class: a stale body. This body names them. Cheaper detector: `tools/pr/prepr.sh --body-check`, run here before the handoff.
- `gate`, job 128558742793 (run 42419763628), job 128558744431 (run 42419764212) and job 128558363773 (the edit-run re-run 42420070733). Class: the gate summarising the reds above, and the mutual edit-run deferral. Answer: no separate one. The edit-run gate stays red until the code run at the new head is green, and this pass does not chase it.
- `governance / instrument-self-tests`, job 128558742016: `cancelled`, not a failure. It was cut short with its run. It is outside the merge train's required contexts (owner ruling 2026-11-07).
- `tests / nightly-status` read success at this head (job 128558777253), so none is owed at this head.

The reds on earlier commits of this branch were each answered in round 5. They are carried unchanged:
- `tests / nightly-status` job 128432803216 (run 42372900036). Class: it grades main's last Nightly, not this diff. This diff reaches nothing that check reads, and the check is outside the merge train's required contexts (owner ruling 2026-11-07). Answer: none owed.
- `tests / mutation`, red twice at 8b7a1cd5d (job 128340143256 in run 42350619717, and job 128356124134 in run 42350614102), and red at 0260beb41 (job 128303788367): `MUTATION TABLE REFUSED -- 16 unpinned site(s) added by this diff`. Class: real survivors. Answer: the previous pass added the checks, pinned 14 sites with `--pin-killed` and recorded 2 as equivalent, and `tests / mutation` job 128432836286 read success at 97786d25. Cheaper detector: prepr.sh step 6d lists added unpinned sites locally, but it cannot tell a site some driver already kills from one no driver kills; only the pin drive can, at minutes per mutant. So none exists.
- `tests / mutation-autofix`, red at 0260beb41 (job 128335810798): `mutation-autofix: changed -- 16 added site(s) left alive`, the same 16 sites. Class: a survivor is red by design (ci-autofix.md). Answer: the same as the bullet above. Cheaper detector: none; it is the detector.
- `governance / policy-docs`, red at 0260beb41 (job 128303788457): `SELF-TEST FAILED SessionStart .claude/hooks/session-start.sh 23 passed, 1 failed`. Class: inherited from main. The branch changes no file under .claude/, and 8b7a1cd5d, which carried main's session-start.sh change, read success (job 128356124119). Answer: none owed by this diff.

## Forward-carry

none

## Friction

- handoff-wip: stale: `refs/heads/handoff-wip/r10-why-now-widget` still holds 4d318d4bb, an earlier session's step that is not an ancestor of this branch. A fast-forward step push is refused, and this seat may not force it, so no step was pushed. The only pushes are the return refs. Carry: dismissed: the brief's end-of-run delete clears it
- ci-predict-inprocess-import: unenforced: step 6d's predictor names an INERT read only for a new harness beside a glob-reading script, or a new top-level import into a closure. It did not predict features.py's in-process import of an INERT harness, which only a recording sees. Carry: dismissed: no live owner, raised here for orchestrator triage

