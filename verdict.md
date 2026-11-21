Fix review: merge e9ad13fa58e02965bb5eb772b19535c09c9523c6

bus-nonce: e01087be6bef541cd24f923dbd345715
pending-ci: gate

## Scope

Round 4, delta review (owner ruling, tvofi 2026-11-09; orchestrator note): `git diff 98cb43e750457b41ae6feb9a0c56cf1d6728e201 e9ad13fa58e02965bb5eb772b19535c09c9523c6`, the prior block's survivor, and the live required checks. `review_carry.py 98cb43e7 e9ad13fa` prints FRESH-REVIEW. The PR's own delta: b4091e0b59 (tests/open_meteo.py), c995a3255c (tests/entities.py), three CI pin commits (tests/mutation_ledger), and main merges. One merge, 7fbdeceef7, hand-resolves a conflict in `custom_components/heatpump_optimizer/__init__.py` `async_migrate_entry` (this PR's number repair against main's 7.2 key placement, #3817). That production resolution puts reviewed functionality at a risk CI would not obviously catch, so the review widened to exactly that function.

## Evidence

- Prior block `mutation-vacuous` at 98cb43e7, `open_meteo.py:256` `if len(kept) < 2:` loosened to `< 1`: now killed. At e9ad13fa, unmutated `tests/open_meteo.py` gives `ALL OPEN-METEO CHECKS PASSED`, rc=0 (ev/m12-baseline.txt). With `< 1`, `<= 0` and `== 0`, each run gives rc=1 and `FAIL a lone sample left after the year-1 drop is no series: mean_over claims no window [times=(datetime.datetime(2026, 8, 21, 0, 0, tzinfo=datetime.timezone.utc),) resolution=739848 days, 0:00:00]` (ev/m12-mutants.txt). The output matches the body's quoted line exactly.
- Null control of b4091e0b59: "the lone-sample check reads a value once a second sample is kept (null control)" reads `ok` unmutated and under all three mutants, so the new check does not fail on every block.
- Merge resolution 7fbdeceef7 (ev/remerge-7fbdeceef-production.txt): `placed(repaired_numbers(effective, repairs))` repairs first, then places. A shadowed key in data no longer survives, and dropped keys take their default. My own harness (the reviewer's, not the finder's; ev/migrate_resolution_harness.py, venv-ha) drives `async_migrate_entry` at the head. For the entry `{min_temperature:"abc", dhw_tank_volume:200}` plus options `{silent_mode_power_fraction:"abc"}`, it gives data `{}` and options `{dhw_tank_volume:200.0, silent_mode_power_fraction:'abc'}` with one warning. `"19.5"` gives `19.5`, and a healthy entry is unchanged in effect. Mutant `placed(effective)`, with the repair dropped, keeps `min_temperature:'abc'` and `'19.5'` as text, so the harness tells the resolution apart from that mutant (ev/migrate-resolution-harness.txt). c995a3255c's updated checks (`_mig_bad.data == {}`, options without `min_temperature`) assert exactly this placement.
- `tests/entities.py` could not run on this host: venv-ci lacks `homeassistant`, and venv-ha lacks `paho` (ev/entities-local-env-error.txt). Its result at this head is cited from CI's tests lanes below.
- All four main merges' `--remerge-diff` are empty except 7fbdeceef7 (above). `git merge-tree --write-tree origin/main e9ad13fa` exits 0.
- `VERSION`, the manifest version, `RELEASE_NOTES.md` and both claim files are untouched in the three-dot diff.
- The PR body's `## Head` names e9ad13fa58e02965bb5eb772b19535c09c9523c6, the head measured. The body's `## Re-cut` records round four.
- Roles contract at merge base vs origin/main: no diff (current).
- CI: see the classify line under `## CI`.

## CI

- `merge_train.py classify e9ad13fa58e02965bb5eb772b19535c09c9523c6 --pr 3734` polled from 16:22:44Z to 16:49:50Z, every ~80 s: every run printed `WAIT e9ad13fa58e02965bb5eb772b19535c09c9523c6 pending: gate red: none` (ev/classify-log.txt). After ~30 minutes the verdict is returned with `pending-ci: gate`, per the brief.
- Live check runs at 16:49Z: `tests / fast (3.14)`, `tests / coverage`, `tests / closures`, `tests / mutation` and `codeql / Analyze (python)` were still in_progress. `governance / instrument-self-tests` was success (job 136904206217), which settles the review packet's `introduced-red: unreadable` refusal. The `arch-score`, `budget-raise-gate`, `hassfest`, `validate-hacs`, `policy-docs`, `wave-script`, `briefs`, `closure-scope`, `typing`, `browser` and `arch-instrument` jobs were success. The concluded `gate` failure (job 136903649588) belongs to the older run 44570846102; classify reads it as pending, not red.
- No owed red is open: classify reports `red: none`, so no `## Red checks` answer is owed.

## Notes

- Note: round: this is round four; the body's `## Re-cut` states the re-cut fixer.md owes.
