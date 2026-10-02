Fix review: blocked e81eb129ef803edaa2865610bb243d866d8b9f7b briefs-red: the diff's tests/doc_claims.py edit moves a carry-1645.json citation and turns CI briefs red; the body says no red check

PR #1839 (R9-EG-B2), round 1. Measured: code head b89293533431bd5e5c6cc81943bbb874582dae55. The live head e81eb129 is that tree plus docs/delivery/1839.md only (`git diff --stat b8929353 e81eb129`), so it is a strict carry. Merge base and origin/main: 777c2318. The tools/audit/briefs diff against main is empty.

## Blocking

- CI `briefs` (job 110707606014, run 36962989283) is red at e81eb129. Its one error that is new against main is `[carry-1645.json carry 0] path:line: tests/doc_claims.py:458: 'check_simulate_plan_fields' not found near tests/doc_claims.py:458; found at line 552 instead`.
- Reproduced locally with `node .claude/workflows/brief_lint.mjs`: rc=0 at 777c2318 and rc=1 at b8929353. The only line that differs between the two error sets is the one above (brief_lint_base_777c2318.log, brief_lint_head_b8929353.log).
- Cause: this diff edits tests/doc_claims.py, which moves `check_simulate_plan_fields` from line 547 to line 552. `.claude/workflows/carry-1645.json` cites the old position.
- Fix: re-measure and re-cite the tests/doc_claims.py lines in carry-1645.json at the new head, then re-run brief_lint.mjs to rc=0.
- The body's "Red checks" section must then name `briefs` and answer it (fix-review.md step 11). The cheaper detector already exists and takes about 3 s: run brief_lint.mjs locally before handoff. The scoped gate does not run it.

## Verified, which survives a re-cut that changes only carry-1645.json

RESULT identity-snapshot: 75 entities (sensor 59, binary_sensor 6, button 4, switch 4, climate 1, datetime 1). The rows are byte-identical across base en, base sv, head en and head sv (cmp, ALL_IDENTICAL).
- Instrument: the fixer's identity_snapshot.py (sha1 003ab58c…). No finder's harness is committed, and the brief names only its shape.
- My own perturbation: object id derived from `key` instead of the translation key. The head sv snapshot then moves 46 of 75 rows, so the instrument detects identity changes.

RESULT private-reaches: 0 at head in entity, sensor, binary_sensor, button, switch, climate, datetime and diagnostics. I counted them with an independent grep, not the fixer's scan. diagnostics keeps 6 reaches with no accessor, as the body says (R9-EG-B6).
- `effective_config` is the same frozen `{**entry.data, **entry.options}` (coordinator.py 2308, CoordinatorContext frozen, never mutated). The climate and binary_sensor copies were therefore value-identical.

RESULT deleted-properties: last_optimization, next_optimization, solar_radiation and floor_return_temp have no attribute reader anywhere in the tree: package, tests, card JS, blueprints and docs. The remaining hits are payload keys, private members or entity-id strings.

RESULT tests at head (Python 3.13.14, requirements-ci):
- features: ALL 3650 PASSED.
- structure: RATCHET PASSED.
- doc_claims: 84 PASSED.
- harness_headers: 94 PASSED.
- entities: 2 of 2060 failed, the same 2 as at base (2 of 2055). Both are docs/HANDOVER.md `updated-for` ancestry checks, an artifact of this clone's history and not this diff.

RESULT mutants (my own, tests/entities.py at head): 7 of 8 killed.
- MA (binary_sensor reads `_mold_floor_series`), MB (sensor reads `_thermal_params`), MC (climate private merge) and MG (input_configured reads `_config`) are killed by the EG-B2 private-read check.
- MD (unique-id separator) is killed by the unique-id-keeps checks, with 24 FAIL.
- ME (object id from key) is killed by P6 B (6 dangling, then a StopIteration crash).
- MF (the thermal_model view aimed at `_thermal_params`) is killed by an AttributeError crash in sensor.py:632, not by a named check.
- MH (diagnostics `mode` reverted to `_mode`) SURVIVES. It is value-equivalent: the `mode` property returns `_mode`. That makes it an equivalent mutant, not a gap.

RESULT budgets: structure_budgets.json moves only down (coordinator_loc and max_class_loc 9006 to 8992, coordinator_methods 224 to 220, cut_fetch 118 to 117). CI budget-raise-gate is green.
- VERSION, the manifest and the RELEASE_NOTES heading are untouched.

CI at e81eb129 when I posted: typing, closure-scope, browser, nightly-status, delivery-status, policy-docs, env-matrix, instrument-self-tests, CodeQL, hassfest, validate-hacs, pr-contract and budget-raise-gate are green. fast (3.14), mutation, closures and coverage were still running and are not cited.

Not re-derived: the archscore deltas, which are report-only and from the fixer's exported prototype. I did not re-run them.
