Triage batch 187 rules P609 (queue line 288, the train's undraft gap), 2026-11-11. It holds one ruling.

- **P609, ACCEPT: TRAIN-UNDRAFT-EVERY-ROUTE, as a carry on R10-TRAIN-RESIDUE-P2.** `undraft` acts only on a draft flag that `add` alone sets, so `--queue`-file and auto-admitted entries never undraft.
  - #3425's relaunch batch logged 20 "still a draft" refusals and burned 2 of 3 recarries. `train.log` holds 78 such attempts over 8 PRs.
  - The card records the flag at batch admission on every route.
  - It treats "still a draft" as a state: undraft once, or stop as a hold, never 8 retries.

The diff is one file against the merge base: `dev/programme/triage/s6-batch187.md`, the ruling. No product behaviour changes.

## Head

`5a3338ebdeab74317101793f7eec279b9ebe4004`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P609 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P609 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P610 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ee64358be7...5a3338ebdeab74317101793f7eec279b9ebe4004`: 1 file, 1 commit.
- The figures come from the live `train.log`, `queue-add.jsonl`, the merge seat's `q-relaunch.json`, #3425's issue events, and `merge_train.py` at `cbd23f1c8b`, as cited in P609.

## Red checks

none

## Forward-carry

none

## Friction

none
