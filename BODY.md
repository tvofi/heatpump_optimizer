Triage batch 190 rules P612 (queue line 290, the local beatd code-freshness arm), 2026-11-11. It holds one ruling.

- **P612, ACCEPT narrowed: BEAT-FRESHNESS-ARM, a local fix with no roster group.** The arm has not fired since 2026-11-10T12:55Z, through 5 manual rotations today.
  - Its guard samples one instant every 15 min. A job is running at 71-76% of those instants: `pulse` 59% of the time, `roster-drain` 30%.
  - Idle runs of 60 s or more come about 9.3 an hour, so the fix polls for up to 15 min for an idle read and logs a deferral.
  - The relaunch also omits the daemon's `--jobs` table; the fix relaunches with the running argv.
  - The P581 carry is not pulled forward: R10-SEAT-IDENTITY-P5 is not started and waits behind R10-TICK-RESIDUE, which is still open and shares `beat_jobs.py`.

The diff is one file against the merge base: `dev/programme/triage/s6-batch190.md`, the ruling. No product behaviour changes.

## Head

`eff68642ed05b32e55725da5a2bee1879539ea90`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P612 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P612 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P613 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ee64358be7...eff68642ed05b32e55725da5a2bee1879539ea90`: 1 file, 1 commit.
- The figures come from the beatd journal, the events file, `beat_extras.sh`, the live `beatd.py status` and daemon argv at 11:48Z, and the roster, as cited in P612.

## Red checks

none

## Forward-carry

none

## Friction

none
