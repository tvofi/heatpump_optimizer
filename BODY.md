replay_doc.py's number shape `_number` (every numeric attribute and price-series value) and its coordinate cut in `clean_value` kept NaN and both infinities, where `replay_doc.numeric` (const.finite_float's domain, written out because the export loads this file with no sibling) refuses them. Both now take `numeric`'s test. Group R11-LATE-P2-REPLAY-FINITE, late class sweep P2, seam F16 `replay_doc._number` (beyond_finding).

The coordinate cut was not named by the sweep: it is the same fact in the same file, returned by the enumeration rule below, so it is built here, not carried.

Alternatives: importing `const.finite_float` is refused by the file's own contract (tests/debug_collect.py pins that replay_doc imports the standard library alone); a second `math.isfinite` call would be a parallel copy of the test `numeric` already owns, so both seams call `numeric`.

## Head

889e901bd3694c3841a1f6247a06f2d6a271d0a5, merge base dbdc71faea358a95a7b33840ed252b0d8a646a31 (origin/main at dbdc71faea358a95a7b33840ed252b0d8a646a31, 2026-11-26T08:18Z).

## Mutation proof

- `_number`: predicate `numeric(value)` replaced by `not isinstance(value, bool)` (the base's line), `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` in a `git archive` copy of the head: `FAIL replay_doc._number keeps a value exactly when it is a number replay_doc.numeric admits, so a NaN or infinite attribute or series value is cut`, 1 of 166 failed.
- coordinate: `if numeric(value):` replaced by `if not isinstance(value, str) or numeric(value):`, same command: `FAIL replay_doc.clean_value nulls a coordinate replay_doc.numeric refuses, NaN and an infinity in any spelling, and records the text it nulled`, 1 of 167 failed.

## Null control

At the merge base both new checks fail on the unmodified tree (written first, run before each fix): `_number` kept `nan` and `inf` and the series kept three non-finite rows; `clean_value` returned `nan`/`inf` for the coordinates. The finder's harness reads the seam at the base and not at the head; under its own `--perturb` (the sibling's guard given to the seam in memory) it reads clean at the base, so it moves on its perturbation.

## Figures

- Finder's harness: `$EXPORT/dev/audit/rounds/round11/D14/sweep-P2/probes_p2.py` (sha1 5058a46432166867f8e75a5d4846acea20d0b752; `$EXPORT` is a `git archive` export of the measured tree with the file from `git show 872510cd3e:dev/audit/rounds/round11/sweep/P2/D14-sweep-P2/probes_p2.py` placed at that path, which its `ROOT = parents[6]` expects), run with `PYTHONPATH=tests/hastub`: base dbdc71faea `FAIL replay_doc._number -- 3 of 3 non-finite probes kept where finite_float refuses`; first fix commit 7bba499631 `pass replay_doc._number -- 0 of 3 non-finite probes kept`; base under `--perturb` `pass ... 0 of 3`. Its other probes are other groups' seams, not this diff's.
- Enumeration rule for the set the claim quantifies over (every number coercion in replay_doc.py): `grep -n "float(\|isinstance([a-z_]*, (int, float" custom_components/heatpump_optimizer/replay_doc.py` at the base. Dispositions: `numeric` (the owner copy, guarded, census replay_numeric_domain); `json_decimal_places` (counts a spelling's decimals, writes no value: not applicable); `text_ok` (decides whether text may leave the install, writes no number: not applicable); `clean_value` coordinate (closed in this diff); `_number` (closed in this diff); `_scan_leaf` (leak scan of a kept number, writes none: not applicable).
- Registry: `tests/entities.py` `_P2_CENSUSES` gains `replay_number_finite` and `replay_coordinate_finite`, each naming its check in tests/debug_collect.py.
- Scoped gate: `python3 tests/closure.py select --diff dbdc71faea358a95a7b33840ed252b0d8a646a31` prints `MODE: SCOPED -- 15 script(s) run, 19 scoped out`; each named script run with `PYTHONPATH=tests/hastub GOLDEN_MODE=drift` at the head exits 0.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Architecture score: `python3 tools/audit/archscore/score.py --diff dbdc71faea358a95a7b33840ed252b0d8a646a31 HEAD`: dS +0.0000 NULL.

## Red checks

- `tests / mutation`, predicted by prepr step 6d (`ci_predict.py`), not yet run on a pull request: (1) two ledger pins, `replay_doc.py:_number BOOLOP 59b66cd2` and `GUARD_OFF 59b66cd2`, named the pre-fix line this branch rewrote (STALE PIN); repaired here by deleting both files in commit "mutation ledger: drop the two _number pins", after which `python3 tools/pr/ci_predict.py --base origin/main --only mutation` predicts no red. (2) the four added sites under `## Unpinned sites`, a warning the `mutation-autofix` lane pins. Cheaper detector: prepr step 6d is the cheaper detector and it caught both before the push; none cheaper is owed.

## Unpinned sites

Each killed by tests/debug_collect.py in prepr's `diff mutants` step (no survivor among the diff's first 40 mutants under `env PYTHONPATH=tests/hastub python3 tests/debug_collect.py`); disposition: pinned by `mutation-autofix`, which mutates `custom_components/`.

- `custom_components/heatpump_optimizer/replay_doc.py:244 GUARD_OFF` (`if numeric(value):`, the coordinate cut)
- `custom_components/heatpump_optimizer/replay_doc.py:247 GUARD_OFF` (`if isinstance(value, str):`, the coordinate text record)
- `custom_components/heatpump_optimizer/replay_doc.py:271 BOOLOP` (`_number`'s predicate)
- `custom_components/heatpump_optimizer/replay_doc.py:271 GUARD_OFF` (`_number`'s predicate)

## Forward-carry

none

## Friction

none
