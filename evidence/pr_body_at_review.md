R10-ARCHSCORE-COVERAGE, part 1 of 5: ARCH-s3's three instrument holes in the architecture score (roster item 5).

Closes #2228.
Part of #2235.
Part of #2259.

The roster group is size L with seven items and six findings, past `fixer.md`'s preamble scope (one subsystem, at most five findings, about 400 production lines), so it lands as a sequence of pull requests on `tools/audit/archscore/`, each with its own calibration cases. This one is item 5 (D7-s3-51, D7-s3-52, D7-s3-53). The rest follow: part 2, items 4 and 7 (the hub role engine: aliases through zero-argument readers and attribute rebinds, D7-s1-83; event-callback hub writes, ARCH2-s2 P4); part 3, item 1 (layering and import closure); part 4, items 2 and 3 (card coverage, D7-s3-02; dict-literal clones); part 5, item 6 (the shape census, calibrated first). #2259 closes with the last part. #2235 stays open past this group: D7-s1-01 and D7-s3-01 are `tests/structure.py`'s, which this group does not touch.

What changes, one definition per hole, each a counter with an ablation switch (`ARCHSCORE_ABLATE`):

- **C14**: the payload census types a parameter annotated with a package class (`X`, `X | None`, `Optional[X]`, a string form) as an instance of it (`untyped_payload_keys.Flow.seed`). Before, it typed a value only through the coordinator's attributes, so `_fold_away(state: away_mode.AwayState)` hid the ten away keys (D7-s3-51).
- **C1b**: `is_any` reads every spelling of "no type" as untyped: a union with an `Any` member, `Optional` and `Annotated` around one, a string annotation, and a package alias of one (`any_aliases` and `resolve_aliases`, to a fixed point, `TypeAlias` and `type X = ...` included). Before, eight spellings read as typed (D7-s3-52).
- **C6b**: `family_orphan_overrides` counts an override whose target is not the first word of the entity's English name. A redundant override naming the key's own first-token family moves nothing and is not counted. Before, two neighbours declared into an invented family passed the size test (D7-s3-53).

Calibration: each counter has a planted BAD and GOOD pair (`a3_payload_annotated_param_*`, `a3_payload_any_spelling_*`, `a3_family_lead_homing_*`, plus a redundant-override NULL) and a red-team attempt (`rt_16`, `rt_17`, `rt_18`). The pin holds no instance of any of them, so `planted/controls.py` gains `on`, which names the case an arm is applied on top of. It replaces `fix_on`, which could only stack a fix on its own control, and `a3_import_cycles_fix` uses it with an unchanged verdict. `expected.json` gains exactly those ten cases. No weight changed, no recorded verdict moved, and no weight perturbation moves one.

Alternatives considered: the prototype patch 02 kept the alias set in module-level mutable state (`ANY_ALIASES`) that `typed_dicts` rewrote on every call. That lost to an alias resolver taking the package, which keeps `is_any` a pure predicate over one annotation. It also keeps the finder's `U.is_any = lambda a: False` ablation working. Seeding annotated parameters in the shared `Engine.seed_env` lost to seeding them in the payload census alone: the shared seed feeds `hub_solve_writes` and `shared_inplace_writes` propagation, which this item has no calibration for. Part 2 owns that engine.

## Head

`92f549f9cf7339627c3d8acda08c6d4eec0061b1` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2293.md`. The authored code head is `4c6f984e239768e415a91afbbfd93ac310c8a2d5`.

`4c6f984e239768e415a91afbbfd93ac310c8a2d5` (origin/main `586455741` merged in; measured `2026-10-15T18:41Z`)

## Mutation proof

Each mutant was applied in place on the committed head, run, and restored with `git checkout`. The runner was `calibrate.py --only <the ten new cases and their base a3_untyped_payload_keys_fix,...>` against the recorded `expected.json`, and for M1 also `tests/arch_score_head.py`. M0 (no mutation) printed no MOVED line.

- M1, C14: `Flow.env` seeds with `self.eng.seed_env(fn)` instead of `self.seed(fn)`. MOVED `a3_payload_annotated_param_control` (WORSENS -> IMPROVES) and `rt_16_payload_annotated_helper` (NULL -> IMPROVES). `tests/arch_score_head.py`: FAIL "the payload census sees every key AwayState.as_dict publishes", 10 unseen, 1 of 16 head checks failed.
- M2, C1b: `is_any`'s union branch deleted. MOVED `a3_payload_any_spelling_control` (WORSENS -> NULL), `a3_payload_any_spelling_fix` (IMPROVES -> NULL) and `rt_17_typeddict_any_spellings` (NULL -> IMPROVES).
- M3, C6b: the lead clause of `family_orphan_overrides` replaced by `False`. MOVED `a3_family_lead_homing_control` (WORSENS -> NULL) and `rt_18_family_invented_pair` (WORSENS -> IMPROVES).

Ablation, per counter (the same ten cases, `ARCHSCORE_ABLATE=C14|C1b|C6b`): each switch reopens its own attempt, which reads IMPROVES (rt_16 +0.6228, rt_17 +50.8607, rt_18 +2.2686), and leaves the other two closed.

## Null control

- The unmodified base reads every new case wrong: run with the head's cases on base code, `a3_payload_annotated_param_control` (BAD) reads IMPROVES, both `a3_payload_any_spelling_*` arms read NULL, `a3_family_lead_homing_control` (BAD) reads NULL, and all three attempts read IMPROVES.
- Honest code does not trip the new definitions. No recorded corpus, planted or red-team verdict moved. The corpus vectors re-measured for `untyped_payload_keys` and `family_orphan_overrides` are byte-identical to the stored ones (`git diff` of `corpus_vectors.json` empty after `--measure-corpus --only-metric untyped_payload_keys,family_orphan_overrides`). Today's tree reads `untyped_payload_keys` 0 and `family_orphan_overrides` 0 at both ends. `a3_family_lead_homing_null` (a redundant override) reads NULL.
- The companion harness's type-stating controls (`float`, `float | None`, `Optional[float]`, `"float"`, `Annotated[float, "k"]`, `dict[str, Any]`) read 0 at both ends. With C1b switched off, the eight spellings read 0 again and bare `Any` reads 6.

## Figures

Finder's harnesses run from the round-10 baseline export (`$EXPORT` = `git archive e0a2e91bd dev/audit/rounds/round10/D7/arch-s3`), at the base `694120d5a` and at the head, `PYTHONPATH=tests/hastub`:

- `$EXPORT/dev/audit/rounds/round10/D7/arch-s3/payload_census_coverage.py --perturb` (sha1 8a7178be3d2f6237404c2f4d8c3229e9f8ede9cf): blind_keys 10 -> 0; census_keys 166 -> 176; perturb_away_keys_census_sees 0 -> 10; perturb_headline_untyped 0 -> 10.
- `$EXPORT/dev/audit/rounds/round10/D7/arch-s3/payload_any_spellings.py` (sha1 862539deae7a4cddb4a3883e590855eedf93d06b): untyped_with_Any_or_None, _Optional_Any, _string_Any, _alias_Any 0 -> 6 each; float 0 at both ends; ablated_C1_untyped_with_Any 0 at both ends.
- `$EXPORT/dev/audit/rounds/round10/D7/arch-s3/family_pair_homing.py` (sha1 08c9c94f66aa12dc38aea18182ad601ed7e6642b): game_family_orphan_overrides 0 -> 2; honest_family_orphan_overrides 0 at both ends.
- Companion, in tree for the later seats, `python3 dev/audit/harnesses/r10_archscore_any_spellings.py`. It drives all eight spellings the catch-up judge listed plus a `TypeAlias` (the finder's harness drives four): each of the nine reads 0 -> 6, the six type-stating controls read 0 at both ends, and the C1b-off null reads 0 for all nine at the head.
- Calibration: `python3 tools/audit/archscore/calibrate.py` at the head. The rule: only the ten new cases are not in the base's `expected.json`, every new case classifies as its label says, and no `SENSITIVE` line is printed. The totals are the instrument's.
- Mutation and ablation figures above: `calibrate.py --only ...` with the mutant applied or `ARCHSCORE_ABLATE` set.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`, MODE: SCOPED. It names `tests/arch_score.py`, `tests/arch_score_head.py` and `tests/entities.py`, each run green locally, plus `run.sh`'s `run_always` scripts (`tests/harness_headers.py`, `tests/layout.py`, `tests/closure.py selftest`, `tests/env_drift.py --claims-only`). `python3 tests/structure.py`: passed, not touched. `python3 tools/audit/seat/tmp_paths.py --check`: 0 refused.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`. The package is unchanged, so the gate's own measure of the change is the instrument's, run from the base.

Class seams (step 8). The rule is every reader of an annotation's "no type" (`grep -n "is_any" -r tools/audit/archscore`) and every resolver of a parameter's type in the payload census. `is_any` has two readers in `typed_dicts` (class form and functional form): both route through `resolve_aliases` in this diff. Its ablation stub in `vector.py` is kept. The census's one seed site is `Flow.env`, closed. `family_orphan_overrides` has one caller (`vector.py`), switched. Item 4's hub engine (`common.Engine.seed_env` and `_derive_aliases`) is the distinct finding D7-s1-83, part 2.

## Unpinned sites

n/a for production code: the diff touches `tools/audit/archscore/` and tests only. The new predicates are pinned by the calibration cases and the head check above (M1 to M3 killed).

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

