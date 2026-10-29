Fix review: merge f53ac2a3987e8dbf59ebedd0b708731d767aa5ab

bus-nonce: a55f8b75623768404c28a1e826eadd21

## Findings

None.

## Evidence

- Re-check at head f53ac2a3987e8dbf59ebedd0b708731d767aa5ab (PR head confirmed unchanged via the pulls API). Check-runs read across all pages, saved in ev/check-runs.tsv.
- arch-score / arch-score: success (latest 2026-10-29T14:59:36Z). pr-contract / pr-contract: success (latest 15:00:35Z). gate: success (all three runs, latest 15:01:42Z).
- No other required context is red. The only failure is tests / nightly-status, which is answered in the PR body and is not a required check that blocks. Every other run concluded success or skipped.
- Code and the claim-file resolution delta were not re-reviewed, as instructed; the previous review found the delta sound.
