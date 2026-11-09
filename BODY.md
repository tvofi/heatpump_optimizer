HOTFIX for the required `tests / fast (3.14)` red on `main` at 2f6d699e (run 42655081843, job 129291622423). Cause: a merge skew, not an environment. #3331 (`fix/r10-i18n-de`, merged 2026-11-09 17:24 +01:00) created the German strings from a branch whose last `main` merge (070425a79) contains neither #3360 (72a2acee5, merged 15:32) nor #3372 (b944521a2, merged 16:03); `git merge-base --is-ancestor b944521a2 ebf90bd27^2` exits 1. Each of the three was green on its own head; the merged tree carried keys en and sv had and de lacked:

- `translations/de.json` missed the five keys #3372 added (`flow_heat_c` and `flow_min_lift_k` label and description under `options.step.entities.sections.indoor`, `selector.space_setpoint_unit.options.return`), so claim C112 of `dev/audit/rounds/round4/D6/claims.py` went false and `tests/harness_headers.py` red. #3372 also reworded the en `space_setpoint_unit` and `pump_duty_mode` descriptions; de rendered their old wording, which key parity cannot see, so both are re-translated here too.
- the card's `de` dictionary in `www/heatpump-optimizer-card.js` missed `savings.below_meter_floor` and `savings.meter_floor_note`, which #3360 added to en and sv, so `tests/card.mjs`'s key-for-key check and its null-control check went red.

The fix is the missing German text in both files; no code, no test, no budget moves.

## Head

df316f48f2116bceef6fc79c6fb78017ad81f07a, on merge base 2f6d699e504d6dc0bb6040d99c21c5b015a290e4 (origin/main at 2026-11-09 17:13 UTC).

## Mutation proof

- `de.json`: from the head, delete the one line adding the `flow_min_lift_k` label, then `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` fails exactly CI's three checks: `dev/audit/rounds/round4/D6/claims.py RESULT claims_true matches header [header='123' printed='122']`, `... RESULT claims_false matches header [header='0' printed='1']`, `the executed harnesses leave their committed output byte-identical` (`3 of 112 HARNESS HEADER CHECKS FAILED`). C112 printed `missing={'de': 1, ...} **false**`. Restored.
- card: with the two added `savings.*` lines absent (the tree at a1d3158d), `PYTHONPATH=tests/hastub node tests/card.mjs` fails `every card language is key-for-key with en and keeps en's placeholders` (`de: missing savings.below_meter_floor; de: missing savings.meter_floor_note`) and `and a planted missing key, dropped or unlisted extra placeholder, or extra key in any language fails it (null controls)`; `2 CARD CHECK(S) FAILED`. With them: `ALL CARD CHECKS PASSED`.

## Null control

At 2f6d699e unmodified, `claims.py` prints `claims_true=122` `claims_false=1` with C112 `missing={'de': 5, 'en': 0, 'sv': 0}`, `tests/harness_headers.py` fails the same three checks as CI's log, and `tests/card.mjs` fails the same two checks as the a1d3158d run above. At the head, `claims.py` prints `claims_true=123` `claims_false=0` and leaves `dev/audit/rounds/round4/D6/claims.json` and `claims.md` byte-identical.

## Figures

- the five missing de keys: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`, C112 row, at 2f6d699e (`missing={'de': 5, ...}`) against the head (`missing={'de': 0, ...}`).
- the two missing card keys: `PYTHONPATH=tests/hastub node tests/card.mjs`, at a1d3158d against the head.
- scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED`; every script it names ran green at the head except `tests/golden.py`, whose drift arm `tests/env_drift.py --all` ran green, and `tests/card.mjs` and `tests/card_drift.mjs` (`identical in all 45 states`) were re-run green after the card commit.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at the head.
- seam enumeration (`fixer.md` step 8): the rule is the two key-parity checks themselves, C112 over every `translations/*.json` against `strings.json`, and `tests/card.mjs`'s key-for-key check over every card language against en. Both enumerate every language and both pass at the head, so no third language or dictionary is short.

## Red checks

- `tests / fast (3.14)` on `main` at 2f6d699e: the cause is a merge skew between #3331 and #3360/#3372, each green on its own head. The cheaper detector is the scoped gate run on the merged tree before merging, which already exists: `tests/closures.json` puts both `translations/de.json` and the card in the closures of `tests/harness_headers.py` and `tests/card.mjs`, so a re-proof of #3331's head on a `main` containing #3360 and #3372 would have caught both. Whether the train re-proved #3331's head on that `main`, and why not, is the root-cause seat's to establish (`defect-root-cause.md`); this PR builds no countermeasure.
- the same cause turned a third script red: `tests/entities.py` at 2f6d699e fails `de.json has exactly strings.json's keys` and the two `every flow field has a label/description where the frontend looks, in de.json` checks (`3 of 2707 ENTITY CHECKS FAILED`, `RUN_PART=fast PYTHONPATH=tests/hastub bash tests/run.sh`); at the head it passes.
- local artefacts, not CI reds: that unscoped run at 2f6d699e also failed `tests/stress.py`, every failure reading `origin/main IS this commit ... A tree compared against itself reports no drift` (CI sets `GOLDEN_REF` to the first parent), and `tests/golden.py` under `GOLDEN_MODE=strict` on solver floats (`CLAUDE.md` rule 3; CI's fast lane runs `tests/env_drift.py --all` instead, green at the head).

## Forward-carry

none

## Friction

none
