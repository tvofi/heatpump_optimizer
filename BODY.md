Triage batch 193 rules P615 (queue line 293, the main nightly red of run 42934263129), 2026-11-11. It holds one ruling.

- **P615, ACCEPT: new hotfix group R10-HOTFIX-REPLAY-CLASS-CUT** (S, lane C, severity high, opus). The ruling is a re-record down, not a regression.
  - `slow` failed `synthetic-dhw-only.json: cycle_cost` at cpu_ratio 1.7266 against the ref40 class budget 3.9874, and the doubled arm's 3.5914 is under the same cap.
  - ref40 rests on 2 clean draws from 11-04 and 11-05 (2.76-2.88), both before `17bb738485` (one BLAS ThreadpoolController), which cut the cycle CPU. The cut factor measured from CI is 0.612-0.664.
  - No replay file or budget changed between `b8f67a7751` (last green) and `d08ed31049`. The ruler moved from ref47 (45.75 ms) to ref40 (41.2 ms).
  - Second instance: `fa3ab3e646` re-recorded only ref47 after the cut. Projected, six of seven classes, holding 58% of the 117 draw jobs, fall under their floors, and appending one draw cannot recover ref23 or ref31 (their pre-cut spreads are 1.84x and 1.74x). So the group re-derives every class with the pre-cut draws projected by an interleaved one-box cut factor.
  - mutation-ledger (3): the hosted runner lost communication 1h44m in. No code cause, so it is a re-run with no group.

The diff is one file against the merge base: `dev/programme/triage/s6-batch193.md`, the ruling. No product behaviour changes.

## Head

`9698b45f586d8fe57223d4fc6ccd15aa7c5fd808`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P615 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P615 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P616 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ee64358be7...9698b45f586d8fe57223d4fc6ccd15aa7c5fd808`: 1 file, 1 commit. `tests/layout.py --guard`: 0 refusals.
- The figures come from the `slow` logs of jobs 130240315059 and the 11-10 scheduled run, `tests/replay_cost_draws.tsv` and `tests/replay.py` at `ee64358be7`, and the `mutation-ledger (3)` check-run annotation, as cited in P615.

## Red checks

none

## Forward-carry

none

## Friction

none
