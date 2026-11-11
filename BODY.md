Triage batch 155 rules queue lines 249 and 250, which arrived after batch 154. It holds two rulings: P566, ACCEPT narrowed, and P567, ACCEPT narrowed.

- **P566, ACCEPT narrowed on (b) and (c), repairs of observed wrong behaviour: S14-RELAY-CADENCE.**
  - (a) is rejected, a 120 s tick interval as the default. A tick pass costs about 290 core API calls over the baseline.
  - The shared core budget used 4759 of 5000 in the hour before the change. 120 s adds about 350 calls an hour against about 240 of headroom.
  - (b) is accepted inside `tick_loop.sh`: the relay restarts during the sleep, 120 s after it ends. The standalone `pass --loop` is rejected, because it never re-reads its own script.
  - (c) is accepted keyed on the body's content. `body_push` re-keeps a refused body as a new commit with the same tree every pass (4 commits in an hour for r10-train-residue), so a commit-keyed memo never hits.
  - The holder finding is rejected: it is one instance, and a seat's worktree may be live.
- **P567, ACCEPT narrowed, a class barrier: S14-STALE-GATE-MULTI-SUITE.**
  - Nothing swept 3405. Its code run was a bot-actor dispatch, which fires no `workflow_run`, and it ran the branch's `ci.yml`, which predates `sweep-self` (45155d068e). 9 of 28 open PRs are in that state.
  - The train's `unstale` re-runs deferral reds beside a green code gate, as an amendment to R10-TRAIN-RESIDUE carry 13.
  - `policy_refusal`'s per-name overwrite of the rollup (line 2798) is replaced by an any-red rule.

The diff is one file against the merge base: `dev/programme/triage/s6-batch155.md`, the ruling. No product behaviour changes.

## Head

`e24589a41f62d59271b1db6e1f4f8445485aa682`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- Citations of P566 and P567 pass `triage_refusal`.
- With either verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P568 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 8efacee48d...e24589a41f62d59271b1db6e1f4f8445485aa682`: 1 file.
- The API figures come from `gh api rate_limit` sampled every 20 s with the tick and relay process state.
- The cadence figures come from the TICK-RELAY and TICK-PASS lines of tick-loop.log.
- The run facts come from `gh api` on runs 42933054497 and 42945740958.
- The line numbers come from origin/main `63bcdcaad8`; every cited file is unchanged at `8efacee48d`.

## Red checks

`none`. The merge base is main `8efacee48d`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
