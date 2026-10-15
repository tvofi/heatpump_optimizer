R10-ARCHSCORE-COVERAGE, part 1 of 5: ARCH-s3's three instrument holes in the architecture score (roster item 5).

Closes #2228.
Part of #2235.
Part of #2259.

The roster group is size L with seven items and six findings, past `fixer.md`'s preamble scope (one subsystem, at most five findings, about 400 production lines), so it lands as a sequence of pull requests on `tools/audit/archscore/`, each with its own calibration cases. This one is item 5 (D7-s3-51, D7-s3-52, D7-s3-53). The rest follow: part 2, items 4 and 7 (the hub role engine: aliases through zero-argument readers and attribute rebinds, D7-s1-83; event-callback hub writes, ARCH2-s2 P4); part 3, item 1 (layering and import closure); part 4, items 2 and 3 (card coverage, D7-s3-02; dict-literal clones); part 5, item 6 (the shape census, calibrated first). #2259 closes with the last part. #2235 stays open past this group: D7-s1-01 and D7-s3-01 are `tests/structure.py`'s, which this group does not touch.

What changes, one definition per hole, each a counter with an ablation switch (`ARCHSCORE_ABLATE`):

- **C14**: the payload census types a parameter annotated with a package class as an instance of it (`untyped_payload_keys.Flow.seed`). The class may be spelled with `None` in any form (`X | None`, `None | X`, `Optional[X]`, `Union[X, None]` in either order), inside `Annotated`, or as a string. Before, it typed a value only through the coordinator's attributes, so `_fold_away(state: away_mode.AwayState)` hid the ten away keys (D7-s3-51).
- **C1b**: `is_any` reads every spelling of "no type" as untyped: a union with an `Any` member, `Optional` and `Annotated` around one, a string annotation, and a package alias of one (`any_aliases` and `resolve_aliases`, to a fixed point, `TypeAlias` and `type X = ...` included). Before, eight spellings read as typed (D7-s3-52).
- **C6b**: `family_orphan_overrides` counts an override whose target is not the first word of the entity's English name. A redundant override naming the key's own first-token family moves nothing and is not counted. Before, two neighbours declared into an invented family passed the size test (D7-s3-53).

**Round 2 (the #2293 round-1 review, class-open):** `Flow.seed` unwrapped only `X | None` and `Optional[X]`, so `Union[X, None]`, `Union[None, X]` and `Annotated[X, ..]` reopened attempt 16. Meanwhile the same diff's `is_any` read those spellings as wrappers. The repair is one reader of an annotation's spelling, `annotation_members`. It takes apart the TypedDict qualifiers, `Annotated`, `Optional`, `Union` and `a | b` in any order, and string forms. `is_any` (C1b) and `Flow.seed` (C14) both call it, so the two cannot disagree again. New cases: `rt_16b_payload_union_helper` (`Union[None, X]`), `rt_16c_payload_annotated_param_helper` (`Annotated[X, "x"]`), and the planted arms `a3_payload_annotated_param_spelling_control` (Union), `_control_write` (Annotated) and `_fix`.

Calibration: each counter has a planted BAD and GOOD pair (`a3_payload_annotated_param_*`, `a3_payload_any_spelling_*`, `a3_family_lead_homing_*`, plus a redundant-override NULL) and a red-team attempt (`rt_16`, `rt_16b`, `rt_16c`, `rt_17`, `rt_18`). The pin holds no instance of any of them, so `planted/controls.py` gains `on`, which names the case an arm is applied on top of. It replaces `fix_on`, which could only stack a fix on its own control, and `a3_import_cycles_fix` uses it with an unchanged verdict. `expected.json` gains exactly those fifteen cases (ten in round 1, five in round 2). No weight changed, no recorded verdict moved, and no weight perturbation moves one.

Alternatives considered: the prototype patch 02 kept the alias set in module-level mutable state (`ANY_ALIASES`) that `typed_dicts` rewrote on every call. That lost to an alias resolver taking the package, which keeps `is_any` a pure predicate over one annotation. It also keeps the finder's `U.is_any = lambda a: False` ablation working. Seeding annotated parameters in the shared `Engine.seed_env` lost to seeding them in the payload census alone: the shared seed feeds `hub_solve_writes` and `shared_inplace_writes` propagation, which this item has no calibration for. Part 2 owns that engine.

## Head

`54cb8531b6cbe7576381d0acf68f733e496a115b` merges the authored code head `87d54712cfbd12d6a1b3e4cec2db350c2dbfa221` and then merges origin/main `74cf47b9c` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`87d54712cfbd12d6a1b3e4cec2db350c2dbfa221` (round 2; origin/main `8747bbfc4` merged in; measured `2026-10-15T20:31Z`. Round 1 was reviewed at `92f549f9cf7339627c3d8acda08c6d4eec0061b1`.)

## Mutation proof

Re-run in full on the round-2 head (script `mutate_r2.sh` in the seat's scratch). Each mutant was applied in place on the committed head, run, and restored with `git checkout`. The runner was `calibrate.py --only` the fifteen new cases plus their base `a3_untyped_payload_keys_fix`, against the recorded `expected.json`; M1 also ran `tests/arch_score_head.py`. M0 (no mutation) moved no case it ran. MOVED lines for recorded cases outside `--only` (they read `None` because they were not run) are left out below.

- M1, C14: `Flow.env` seeds with `self.eng.seed_env(fn)` instead of `self.seed(fn)`. MOVED to IMPROVES: `a3_payload_annotated_param_control`, `a3_payload_annotated_param_spelling_control`, `_control_write`, `rt_16`, `rt_16b` and `rt_16c`. `tests/arch_score_head.py`: FAIL "the payload census sees every key AwayState.as_dict publishes", 10 unseen, 1 of 16 head checks failed.
- M2, `annotation_members` no longer takes `a | b` apart. MOVED: `a3_payload_any_spelling_control` (WORSENS -> NULL), `a3_payload_any_spelling_fix` (IMPROVES -> NULL), `rt_17` (NULL -> IMPROVES).
- M4, `annotation_members` no longer takes `Union[..]` apart. MOVED: `a3_payload_annotated_param_spelling_control` (WORSENS -> IMPROVES), `rt_16b` and `rt_17` (NULL -> IMPROVES).
- M5, `Annotated` dropped from the wrappers. MOVED: `a3_payload_annotated_param_spelling_control_write` (WORSENS -> IMPROVES), `rt_16c` and `rt_17` (NULL -> IMPROVES).
- M3, C6b: the lead clause of `family_orphan_overrides` replaced by `False`. MOVED: `a3_family_lead_homing_control` (WORSENS -> NULL), `rt_18` (WORSENS -> IMPROVES).

The unwrapper is shared, so M4 and M5 move a C14 case and a C1b case together.

Ablation (round 1, `ARCHSCORE_ABLATE=C14|C1b|C6b` on the round-1 cases): each switch reopens its own attempt, which reads IMPROVES (rt_16 +0.6228, rt_17 +50.8607, rt_18 +2.2686), and leaves the other two closed.

## Null control

- The unmodified base reads every round-1 case wrong, and the round-1 head reads the round-2 cases wrong. On the round-1 head's `untyped_payload_keys.py`, `a3_payload_annotated_param_spelling_control` and `_control_write` (BAD) read IMPROVES, and `rt_16b` and `rt_16c` read IMPROVES. With the shared unwrapper they read WORSENS, WORSENS, NULL and NULL. Earlier, on the base: run with the head's cases on base code, `a3_payload_annotated_param_control` (BAD) reads IMPROVES, both `a3_payload_any_spelling_*` arms read NULL, `a3_family_lead_homing_control` (BAD) reads NULL, and all three attempts read IMPROVES.
- Honest code does not trip the new definitions. No recorded corpus, planted or red-team verdict moved. The corpus vectors re-measured for `untyped_payload_keys` and `family_orphan_overrides` are byte-identical to the stored ones (`git diff` of `corpus_vectors.json` empty after `--measure-corpus --only-metric untyped_payload_keys,family_orphan_overrides`). Today's tree reads `untyped_payload_keys` 0 and `family_orphan_overrides` 0 at both ends. `a3_family_lead_homing_null` (a redundant override) reads NULL.
- The companion harness's type-stating controls (`float`, `float | None`, `Optional[float]`, `"float"`, `Annotated[float, "k"]`, `dict[str, Any]`) read 0 at both ends. With C1b switched off, the eight spellings read 0 again and bare `Any` reads 6.

## Figures

Finder's harnesses run from the round-10 baseline export (`$EXPORT` = `git archive e0a2e91bd dev/audit/rounds/round10/D7/arch-s3`), at the base `694120d5a` and at the head, `PYTHONPATH=tests/hastub`. At the round-2 head, every RESULT line equals round 1's (`diff` of the RESULT lines is empty):

- `$EXPORT/dev/audit/rounds/round10/D7/arch-s3/payload_census_coverage.py --perturb` (sha1 8a7178be3d2f6237404c2f4d8c3229e9f8ede9cf): blind_keys 10 -> 0; census_keys 166 -> 176; perturb_away_keys_census_sees 0 -> 10; perturb_headline_untyped 0 -> 10.
- `$EXPORT/dev/audit/rounds/round10/D7/arch-s3/payload_any_spellings.py` (sha1 862539deae7a4cddb4a3883e590855eedf93d06b): untyped_with_Any_or_None, _Optional_Any, _string_Any, _alias_Any 0 -> 6 each; float 0 at both ends; ablated_C1_untyped_with_Any 0 at both ends.
- `$EXPORT/dev/audit/rounds/round10/D7/arch-s3/family_pair_homing.py` (sha1 08c9c94f66aa12dc38aea18182ad601ed7e6642b): game_family_orphan_overrides 0 -> 2; honest_family_orphan_overrides 0 at both ends.
- Companion, in tree for the later seats, `python3 dev/audit/harnesses/r10_archscore_any_spellings.py`. It drives all eight spellings the catch-up judge listed plus a `TypeAlias` (the finder's harness drives four): each of the nine reads 0 -> 6, the six type-stating controls read 0 at both ends, and the C1b-off null reads 0 for all nine at the head. These lines are unchanged from round 1 (`diff` empty).
- The same companion's parameter half, added in round 2, spells `_fold_away`'s parameter nine ways. At the round-1 head (`92f549f9c`), `away_keys_seen_param_union_none`, `_union_none_first` and `_annotated` read 0, the review's finding. At the round-2 head all nine read 10 (every key `AwayState.as_dict` publishes). The control `AwayState | int`, not one class, reads 0 at both heads. With C14 off (`FOLLOW_ANNOTATED = False`), all ten read 0.
- Calibration: `python3 tools/audit/archscore/calibrate.py` at the head. The rule: only the fifteen new cases are not in the base's `expected.json` (`calibrate.py --record` in round 2 printed RECORD for the five round-2 cases alone), every new case classifies as its label says, and no `SENSITIVE` line is printed. The totals are the instrument's.
- Mutation and ablation figures above: `calibrate.py --only ...` with the mutant applied or `ARCHSCORE_ABLATE` set.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`, MODE: SCOPED. It names `tests/arch_score.py`, `tests/arch_score_head.py` and `tests/entities.py`, each run green locally, plus `run.sh`'s `run_always` scripts (`tests/harness_headers.py`, `tests/layout.py`, `tests/closure.py selftest`, `tests/env_drift.py --claims-only`). `python3 tests/structure.py`: passed, not touched. `python3 tools/audit/seat/tmp_paths.py --check`: 0 refused.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`. The package is unchanged, so the gate's own measure of the change is the instrument's, run from the base.

Class seams (step 8). Round 1's rule listed sites; the review showed a site can be closed for one spelling and open for its equal. Round 2's rule has two parts. Sites: every reader of an annotation's spelling (`grep -n "annotation_members\|is_any\|\.annotation" tools/audit/archscore/metrics/untyped_payload_keys.py`). Spellings: the companion's two halves, with the members taken apart by the one function both sites now call. `is_any` has two readers in `typed_dicts` (class form and functional form): both route through `resolve_aliases`. Its ablation stub in `vector.py` is kept. The census's one seed site, `Flow.seed`, now reads the parameter through `annotation_members`; `Flow.contract` resolves a TypedDict, not an instance, so it is not this class. Spellings outside `annotation_members`'s grammar (a generic `X[T]`, a `TypeVar` bound, a `Protocol`) resolve to no class, so the census does not follow such a parameter: a residual the companion does not drive. `family_orphan_overrides` has one caller (`vector.py`), switched. Item 4's hub engine (`common.Engine.seed_env` and `_derive_aliases`) is the distinct finding D7-s1-83, part 2.

## Unpinned sites

n/a for production code: the diff touches `tools/audit/archscore/` and tests only. The new predicates are pinned by the calibration cases and the head check above (M1 to M5 killed).

## Architecture score

n/a: no package file changes; the instrument change takes effect after merge (`ABOUT.md`).

## Red checks

none

## Forward-carry

- Item 4 (part 2) re-derives D7-s1-82's score credit on the extended hub census, as the roster carry says (R10-PARAMS-OWNER runs after this group). It stays with this group's later parts, in `dev/programme/rosters/wave-r10-groups.json`'s R10-ARCHSCORE-COVERAGE `carry`.
- For R10-BRIEFS-FOLD: the D7 brief may cite C1b, C6b and C14 (`tools/audit/archscore/ABOUT.md`'s counter table) once this merges. The orchestrator owns the roster edit (`roster_edit.py append-carry`) and was told at handoff.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)

