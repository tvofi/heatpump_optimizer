Triage batch 186 rules P608 (queue lines 286-287, the train policy-refusal reason), 2026-11-11. It holds one ruling.

- **P608, ACCEPT narrowed: TRAIN-POLICY-REASON-STALE-CONTEXT, as a carry on R10-TRAIN-RESIDUE-P2.** `policy_refusal` keeps the last-listed rollup entry per context, not the newest one.
  - At #3445 `7fb8680c`, the newest `gate` is FAILURE, but an older SUCCESS is listed last. The train therefore parked "missing review" while GitHub blocked on a red `gate`.
  - The card reads the newest entry, and treats any in-progress entry as pending.
  - The undraft arm is rejected: #3398 was undrafted and was refused alike. The CodeQL arm is rejected: it is not a required context, since the ruleset requires only `gate`.

The diff is one file against the merge base: `dev/programme/triage/s6-batch186.md`, the ruling. No product behaviour changes.

## Head

`2cb0be58179081fc67201d8d5d96a62ad7d5ecd7`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P608 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P608 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P609 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat cbd23f1c8b...2cb0be58179081fc67201d8d5d96a62ad7d5ecd7`: 1 file, 1 commit.
- The figures come from the live `train.log`, from `gh pr view --json statusCheckRollup` on #3445, #3405 and #3398, from ruleset 23698884, and from `merge_train.py` at `cbd23f1c8b`, as cited in P608.

## Red checks

none

## Forward-carry

none

## Friction

none
