Triage batch 165 rules queue line 261. It holds one ruling.

- **P579, REJECT: TRAIN-REJOIN-WAIT-BLOCKS-SPOOL.**
  - The instance is not a rejoin wait. PR 3355 is the batch's serial entry: parked `[MAIN-MOVED]`, taken down the card-5 no-recarry path, and now in `wait_ci` at its own head while a ci.yml re-run finishes. `Train.rejoin` prints no `beat:` line. Both arms as asked move 0 of 1 instance.
  - The general mechanism, a single-head CI wait holding a non-empty spool, measured over the live train log: in 7 days the pure gain (waits that end in a skip) is 17,228 s, 6.7% of the train's 256,345 wait-s; 9.1% over 26 days; 14.9% even counting every blocked second, merges included.
  - Under the 20% bar for new instrument machinery, in the train's hot file: REJECT. A critical-path-only yield is DEFERRED to a second critical-path instance.

The diff is one file against the merge base: `dev/programme/triage/s6-batch165.md`, the ruling. No product behaviour changes.

## Head

`6c81071a4999897a4d5273756d84ce705eca39c1`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P579 as REJECT.
- A citation of P579 is refused as "not an ACCEPT ruling (REJECT)".
- With P579's verdict flipped to ACCEPT, the same citation passes (`None`).

## Null control

- P580 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".
- In the measurement, 147 of 243 waits had an empty spool for their whole span and count 0 s blocked, so the measure does not count every wait as blocked.

## Figures

- `git diff --stat 8f97247fc1...6c81071a4999897a4d5273756d84ce705eca39c1`: 1 file, 1 commit.
- The wait figures come from one script over the train log's 19,710-line snapshot at 05:30Z: 243 waits, 523,303 wait-s; 96 spool-blocked.
- No API calls.

## Red checks

`none`. The merge base is main `8f97247fc1`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
