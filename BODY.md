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

**This pass (repair for fix review blocked 97786d25, round 2).**
- **The block, as a class.** Every caller of `_build_comfort_bounds` now reads the 4-tuple. The harness caller, `dev/audit/harnesses/r10_demand_overbook.py`'s `_dp_reference`, now reads through a new `comfort_schedule(opt, t, n)`, which unpacks four values. tests/features.py drives `comfort_schedule` directly, so a caller left on the old shape fails a named check instead of raising a ValueError in a lane nobody runs. The census of the class and each seam's disposition is in Figures.
- **Finding 1 (the widget direction against the solver).** The metric text is reworded, not gated. The approved note never claimed that the rows agree with the decision, and it gives no agreement figure to gate on, so the rewording is the path that needs no design ruling. en now opens "The reasons weighing on this hour's plan." and says "A high share means that reason pushes hardest; the plan weighs the whole day's hours together, so the heat pump can still do the opposite this hour." sv is the same, in Swedish. The new text departs from the owner's verbatim strings in carry 1 only in those two sentences. tests/card.mjs refuses "decides the hour" and requires the new clause in both languages.
- **Finding 2.** `why_now` is in `_PlanSensorBase._unrecorded_attributes`, and tests/entities.py checks it beside wood_fuel.
- **Finding 3 (mutants C, D and E).** Each now has a killing check: magnitude order at every step of five solves, with a precondition that some step has an idle push larger than a run push; `_solve_record` handing the solve `away.floor_drop_c`; and the margined comfort floor. The D check builds its own coordinator, so the block runs alone under `features_block.py`.
- **Diff-mutant survivors.** Four survivors of the diff-mutant run were killable, and one new check kills all four.
- **Merge.** origin/main 53273de4 was merged at b550ba375, because `git merge-tree` reported a content conflict in tests/features.py. Both sides had appended a block at the file's end, and both are kept: `git diff origin/main -- tests/features.py` removes no main line except the five `_build_comfort_bounds` unpacks this PR changes.

## Head

0765b49d99cdc40ae66c47f7649cf5cec585cce2, cut from merge base 53273de4d449a990bc29734565f63babada9ff7f.
- At 2026-11-07T21:14Z origin/main was dee8b413fd7da7b07f13e28a93d7d49b4a9e978a. `git merge-tree --write-tree origin/main HEAD` returns rc 0 with no conflict, so main was not merged again (owner ruling 2026-11-07).
- Above 97786d25, this pass adds three commits:
  - b550ba375: the merge of main.
  - 9cde30560: the class fix and findings 1–3.
  - 0765b49d9: one tests/features.py check.
- The scoped gate, entities.py, the card checks, the archscore run and prepr.sh were measured at 9cde30560. `git diff --name-only 9cde30560 0765b49d9` is tests/features.py alone. features.py's why-now block and the full features.py were re-run at 0765b49d9.

## Mutation proof

Each mutant below was applied alone, and the why-now block of tests/features.py was run on its own (`features_block.py`, the command in Figures). The driver applies the edit, runs the block and restores the file.
- The class (the block). Restoring the old 3-tuple unpack:
  - At the harness site (`targets, floors, ceilings = opt._build_comfort_bounds(`) fails "R10-WHY-NOW-WIDGET: r10_demand_overbook.comfort_schedule reads the solve's (target, floor, ceiling)" with `ValueError('too many values to unpack (expected 3, got 4)')`.
  - At the production site (optimizer.py, `comfort_targets, temp_min_bounds, temp_max_bounds = (`), the block's first solve raises the same ValueError and the block exits rc 1.
  - The five older tests/features.py sites are drivers, not code under test. A 3-tuple unpack there raises the same ValueError at module level and aborts features.py.
- Failing first, the harness. At b550ba375 (the merge, before the fix), `PYTHONPATH=tests/hastub:tests python3 dev/audit/harnesses/r10_demand_overbook.py --one owner_i01 dp` exits rc 1 with `ValueError: too many values to unpack (expected 3, got 4)`. The same command passes at 9cde30560; see Figures.
- C (`rows.sort(key=lambda d: -d["weight"])`): FAIL "at every step the rows run largest magnitude first, an idle push ahead of a smaller run push". Its precondition counted 126 crossing steps of the 480 read.
- D (`away_floor_drop_c=None` in `_solve_record`): FAIL "_solve_record hands the solve away.floor_drop_c while away, None at home" (`away None (want 3.0)`).
- E (`comfort_floors = temp_min_bounds` deleted after the margins): FAIL "the drivers' comfort floor is the margined floor, below the mold floor's raise" (`margined [19. 19.]`, want 19.4).
- The diff-mutant survivors made killable here:
  - slot_drivers.py:84 `max(1, …)` -> `max(2, …)`: FAIL "the forecast window floors at one step and clips at -1; comfort clips at -1; step_reasons past the end is None" (reads 0.5).
  - :96 clip -1 -> -2: the same check (reads -2.0).
  - :118 clip -1 -> -2: the same check (reads (-80.0, -20.0)).
  - :143 `<` -> `<=`: the same check (`raised IndexError`).
- Finding 2. Without the sensor line, `"why_now" in sensor.SpaceHeatingPlanSensor._unrecorded_attributes` is False at b550ba375 and True at 9cde30560. The new entities check reads that attribute.
- Finding 1. At b550ba375, with this pass's tests/card.mjs applied over the old card, the card checks FAIL "why-now: every en string has its sv twin, and every driver code has a label and an explanation" (1 CARD CHECK(S) FAILED).
- sensor.py:1637 RETURN_DEL (the override returns None). With it applied, tests/entities.py exits rc 1 with `AttributeError: 'NoneType' object has no attribute 'get'` at its first read of the space plan's attributes (entities.py:2243).
- The previous passes' M1–M14, C1–C9 and the 14 `--pin-killed` sites stand. This pass changes no line they mutate, except the five test-side unpacks above.

## Null control

- A comment-only mutant (`NULL_comment`, slot_drivers.py's DRIVER_CODES comment) survives the block (rc 0).
- The harness at base 53273de4 and at 9cde30560 prints byte-identical RESULT lines, rc 0 both: `dp_learned.gap -0.0006`, `dp_true.gap -0.0012`. So the class fix moves no figure the harness reports.
- tests/entities.py at base 53273de4 fails the same 3 checks as at the head, all workflow probes: the coverage job's cache key, the release ZIP and the Pages workflow. The diff touches no file they read, and those 3 are this box's.
- The unmutated block reads ALL 25 FEATURES BLOCK PASSED.

## Figures

- Class census: `git grep -n '_build_comfort_bounds(' -- custom_components tools tests dev ':!*.tsv'` at 0765b49d9 returns 12 lines:
  - The def (optimizer.py:4000): the 4-tuple.
  - The production caller (optimizer.py:3684): unpacks 4, pinned by every solve.
  - The harness caller (r10_demand_overbook.py:223, `comfort_schedule`): unpacks 4 (closed in this diff), pinned by the comfort_schedule check.
  - The five older tests/features.py drivers (34713, 34724, 34734, 34744, 53042): unpack 4, carried from the previous pass.
  - Four new tests/features.py lines of this pass: three calls and one comment.
  - The excluded `*.tsv` hits are r10_mutant_skip/matrix.tsv's site rows, which are data. The rounds/round7 hits are prose.
  - Dynamic references: `git grep -n 'comfort_bounds' -- . ':!dev/audit/harnesses/r10_mutant_skip' ':!tests/mutation_ledger' ':!dev/audit/rounds'` returns only these call lines. There is no getattr or string reference.
- Harness rc census over every dev/audit/harnesses/ script that imports optimizer, coordinator, away, sensor, payload or slot_drivers, or names `_build_comfort_bounds`. The list rule is the `git grep -l -E` over those names. Each script runs with no arguments and a 300 s cap, at 9cde30560 and at 53273de4. The rule returned 65 scripts, and every one exits with the same rc at the head as at the base: 45 rc 0, 11 rc 1, 4 rc 2 and 5 at the cap (124), so no script changed rc. Run with no arguments, r10_demand_overbook.py takes its default arms and not `--dp`, and its parent exits 0 whatever a child does, so the census cannot see the block. The `--one owner_i01 dp` run below is the one that does.
- Harness `PYTHONPATH=tests/hastub:tests python3 dev/audit/harnesses/r10_demand_overbook.py --one owner_i01 dp` (the finder's `--dp` path):
  - rc 1 at b550ba375 (ValueError).
  - rc 0 at 9cde30560.
  - rc 0 at 53273de4.
  - The RESULT lines at head and base are identical.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at 9cde30560 printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` and `1 TEST SCRIPT(S) FAILED`.
  - The one failed script is tests/entities.py: `3 of 2657 ENTITY CHECKS FAILED`, the 3 workflow probes that also fail at the base (`3 of 2655 ENTITY CHECKS FAILED`, same three names).
  - Every other script reads its pass line, including `ALL 4936 FEATURE CHECKS PASSED`, `ALL CARD CHECKS PASSED`, `ALL 84 OPTIMALITY CHECKS PASSED`, `ALL 113 STRESS CHECKS PASSED` and `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` at 9cde30560.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at 0765b49d9: ALL 4937 FEATURE CHECKS PASSED (4936 at 9cde30560, plus the one check added in 0765b49d9).
- Why-now block alone at 0765b49d9: `env PYTHONPATH=tests/hastub:tests python3 tools/audit/seat/features_block.py --prelude 'from types import SimpleNamespace' --prelude 'from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState' '# --- R10-WHY-NOW-WIDGET: per-slot drivers' '# R10-CLONE-2238 (#2238'` reads ALL 25 FEATURES BLOCK PASSED.
- Diff mutants: `python3 -I tools/audit/seat/mutant_run.py --diff 53273de4d449...HEAD --cmd "<the block command above>" --max-mutants 66 --report-only` at 9cde30560 ran all 66 mutants on the added lines (the count is `--list`'s), in 514 s wall time, with 7 survivors. Each survivor's disposition:
  - sensor.py:1637 RETURN_DEL: killed by tests/entities.py, which is outside this block (Mutation proof).
  - slot_drivers.py:23 GUARD_OFF (`if TYPE_CHECKING` -> `if False`): equivalent. The guarded imports are type-only, under `from __future__ import annotations`.
  - :84, :96, :118 and :143: killed by this pass's new check (Mutation proof).
  - :136 CMP_BOUND (`>=`): equivalent, already triaged at `tests/mutation_ledger/survivor_triage/slot_drivers.py/_direction.CMP_BOUND.23463a3d.json`. The line above it returns neutral for every |weight| < 0.5.
  - Re-run at 0765b49d9 with the same command: 66 mutants, 553 s wall time, 3 survivors (sensor.py:1637 RETURN_DEL, slot_drivers.py:23 GUARD_OFF and slot_drivers.py:136 CMP_BOUND), each dispositioned above.
- `node tests/card.mjs` (after `tests/plan_view.py`): ALL CARD CHECKS PASSED. `node tests/card_drift.mjs origin/main`: `card_drift: 1 state(s) moved and claimed, 44 identical`.
- Claim files: `tests/golden/card_claimed_drift.txt` reads `claims-for: 7.1.5`, which equals VERSION. The merge driver resolved it, and this branch adds only the `score_open` entry. Three-dot `git diff 53273de4...HEAD -- tests/golden/claimed_drift.txt` is empty. VERSION, the manifest version and RELEASE_NOTES.md are untouched.
- `python3 tools/audit/archscore/score.py --diff 53273de4d449a990bc29734565f63babada9ff7f`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `bash tools/pr/prepr.sh` at 9cde30560 without a body: `PRE-PR: 9cde30560… rc=0`, `CI PREDICT: no closures, fast, governance or instrument red predicted against 53273de4d449`. The body run is the one body_push.sh makes.

## Unpinned sites

none. At 9cde30560, step 6d listed no unpinned site that this diff adds. This pass's production change is one string in a frozenset (sensor.py) and a harness function under dev/, and mutation-autofix's lane does not mutate dev/. The diff-mutant survivors are dispositioned under Figures.

## Red checks

At this head: none concluded yet, because 0765b49d9 has not been pushed to the PR branch. At the previous head, 97786d25:
- `gate` job 128404815591 (run 42372899572, 12:46Z), and `gate` jobs 128432994419 and 128433346279 (14:50Z and 14:51Z). Each read `FAIL run(s) [...] at this head are still being judged; their gate decides`. Class: the mutual edit-run deferral (R10-HOTFIX-GATE-BUSY-DEFER), deferring to code run 42372900036. That run's re-run concluded and its gate (job 128439916858) read success. Answer: none owed by this diff; the deferral is the gate working as designed.
- `tests / nightly-status` job 128432803216 (run 42372900036). Class: it grades main's last Nightly, not this diff. This diff reaches nothing that check reads, and the check is outside the merge train's required contexts (owner ruling 2026-11-07). Answer: none owed.
- `tests / mutation`, red twice at 8b7a1cd5d (job 128340143256 in run 42350619717, and job 128356124134 in run 42350614102), and red at 0260beb41 (job 128303788367): `MUTATION TABLE REFUSED -- 16 unpinned site(s) added by this diff`. Class: real survivors. Answer: the previous pass added the checks, pinned 14 sites with `--pin-killed` and recorded 2 as equivalent, and `tests / mutation` job 128432836286 read success at 97786d25. Cheaper detector: prepr.sh step 6d lists added unpinned sites locally, but it cannot tell a site some driver already kills from one no driver kills; only the pin drive can, at minutes per mutant. So none exists.
- `tests / mutation-autofix`, red at 0260beb41 (job 128335810798): `mutation-autofix: changed -- 16 added site(s) left alive`, the same 16 sites. Class: a survivor is red by design (ci-autofix.md). Answer: the same as the bullet above. Cheaper detector: none; it is the detector.
- `governance / policy-docs`, red at 0260beb41 (job 128303788457): `SELF-TEST FAILED SessionStart .claude/hooks/session-start.sh 23 passed, 1 failed`. Class: inherited from main. The branch changes no file under .claude/, and 8b7a1cd5d, which carried main's session-start.sh change, read success (job 128356124119). Answer: none owed by this diff.
- pr-contract at 8b7a1cd5d (jobs 128365328341 and 128371723858), a stale body. It cleared with the re-taken body: pr-contract job 128438880772 read success at 97786d25.

## Forward-carry

none

## Friction

- handoff-wip: stale: `refs/heads/handoff-wip/r10-why-now-widget` still holds 4d318d4bb, an earlier session's step, which is not an ancestor of this branch. A fast-forward step push is refused, and this seat may not force it, so no step was pushed; the branch's only pushes are the return refs. Carry: dismissed: the brief's end-of-run delete clears it
- prepr-6d-mutants: unenforced: with `MUTANT_CMD` spelled as an environment assignment (`PYTHONPATH=… python3 …`), `mutant_run.py --diff` shlex-splits it, and its baseline `Popen` raises `FileNotFoundError` before any mutant runs. prepr.sh step 6d' counts `SURVIVED` lines and never reads mutant_run.py's exit status, so it printed `ok diff mutants no survivor: FileNotFoundError: …` at 9cde30560: a pass on a run that never executed. This pass spelled it `env PYTHONPATH=…`. R10-MUTANT-RUN-DRIVER, which owns step 6d', is done, and a fixer seat files nothing. Carry: dismissed: no live owner, raised here for orchestrator triage
