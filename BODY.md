## What changed

Two commits on origin/main `92588d581`:

1. `git rm dev/programme/carries/carry-2674.json`. Its answer is the #2674 close comment 6555939169, posted after #2674's probe.
2. `dev/programme/delivery/3048.md`: the #3048 waiver sentence added verbatim as its own line below the row. The note held only the one row line, so there was no richer structure to follow.

## Sources

- #2674 close comment 6555939169 (answers the carry file).
- Orchestrator ruling under mandate for item 5017455b (the waiver sentence).

## Deletion check

- `tools/audit/carry_audit.py` reads `dev/programme/carries/` generically and does not name #2674.
- `tests/closures.json` line 1561 still lists the file. I did not edit it, since the brief allows exactly two changes. The closure table is re-recorded by CI.
- `dev/programme/triage/s6-batch1.md` line 49 mentions it in prose only, as history.

## Results

- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `tools/pr/prepr.sh`, rc=1: gate mode SCOPED. Every check was ok or skipped except one REFUSE, `closures`: "failed while being recorded: tests/entities.py (exit 1)". The `ci predict` check reports no red predicted.
- `tests/entities.py` could not run in this container. venv-ci has no `homeassistant`. venv-ha has it but no `paho`, so `custom_components` fails to import (`ModuleNotFoundError: No module named 'paho'`). This is an environment gap and not a result about the diff. Main has the same gap. entities.py is therefore unverified here, and CI's run is the first real reading. The `closures.json` entry for the deleted file is the one thing it might flag.
- main had not moved since the base, so no second prepr run was needed.

## Head

05c2245948d6d1df43679e1b652d849d9912e517

## Mutation proof

n/a: record-only change, no production code or check altered.

## Null control

n/a: nothing quantified; two record edits.

## Figures

none

## Red checks

`closures` (prepr REFUSE): `tests/entities.py` exited 1 because this container lacks `homeassistant`/`paho`, so the recorder could not run. An environment gap, not caused by the diff; no cheaper detector applies. CI runs entities.py with its full environment.

## Forward-carry

none

## Friction

none
