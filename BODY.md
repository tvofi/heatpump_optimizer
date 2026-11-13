HOTFIX (R10 batch 246, P744). Main CI is Linux-only, so a Darwin-only self-test regression (PR 3475: `mutant_run.py` listing /proc) was found only when an opener failed; fourth Darwin-only self-test red (audit class). This adds a `darwin-selftest` beat row: Darwin hosts only, one run per new origin/main tip, heavy-slot lease, a detached worktree the row owns, `prepr.sh --self-test` plus each wired seat self-test, one `darwin-selftest: RED <instrument> <first FAIL line>` per red, nothing when green. No workflow file touched (owner ruling 2026-11-12: macOS checks are local seats or beat rows). It detects after merge and does not prevent; a pre-merge arm is round 11.

Closes: none (no issue; triage P744).

## Head

b63d67cc3d9219b6dca0a53b54f679c045320c44

## Mutation proof

Five mutants in `beat_jobs_selftest.py` MUTANTS, each killed by the named case: `darwin_gate_dropped` (the Darwin gate deleted) by "darwin-selftest null: a non-Darwin host runs nothing and writes nothing"; `darwin_first_fail_is_last_line` (first-FAIL extraction replaced by last line) by "a red self-test is one RED line naming it and its first FAIL line"; `darwin_tip_not_skipped` by "an unchanged tip is skipped"; `darwin_red_dropped` by the RED-line case; `darwin_lease_not_released` by "the heavy slot is held around a detached worktree the row makes and removes".

## Null control

Cases in the same self-test: a non-Darwin host runs nothing and writes nothing (no git call); a clean tip prints nothing and every self-test ran; an unchanged tip is skipped; a new tip runs again; an unreadable origin/main is UNREADABLE and runs nothing.

## Figures

- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: the darwin-selftest cases and mutants above all `ok` at the Head, final line reports zero failed.
- NOT MEASURED: the wall time of one run on a Mac, and the red-then-green demonstration at main 19baca76 (must print RED naming mutant_run.py) versus once the mutant_run.py Darwin hotfix is on main (must print nothing). This seat is Linux, where the row's Darwin gate makes the row run nothing; the stub self-test above drives the row with the platform forced to darwin and is the only evidence. Carry: O1 (the Darwin host operator runs the row once at each end and records both and the wall time).
- Round-end measure (detection lag, refused opens per Darwin red) is owed at round end, not measured here. Carry: O1.

## Red checks

none

## Forward-carry

none

## Friction

none
