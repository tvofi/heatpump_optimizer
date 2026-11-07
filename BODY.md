Triage batch 131 rules on one queue line, P402, `s12-stamp-flush-train-hold-deadlock`.

**P402: ACCEPT narrowed**, to a new fly-in group, R10-FLY-STAMP-FLUSH-HOLD (S, `tools/release/stamp.py`).

- **The defect is real.** `record_flush` does not read `refs/heads/train-hold`. While a hold is younger than `nightly.yml`'s `HOLD_MAX_AGE_S=3600`, every beat it dispatches exits as `skip-train-hold`. Its 3 dispatches go out at about 0, 900 and 1800 s, and it then times out at 7200 s with a message that names no hold. That happened on 2026-11-07: train 37335 was killed, and its hold `b588ae95` stalled the v7.1.5 flush until the orchestrator deleted it by hand (ledger SLIP at 06:22:50Z). Two orphan holds came from kills in about 9 h.
- **Accepted, changed.** The flush names the hold within one poll (60 s), reading it through git with no REST call. It no longer counts a dispatch sent under a live hold, and it dispatches again once the hold clears. It never refuses, because a live train legitimately holds the beat and can merge the record PR itself. On the 11-07 instance that is 22 min off the stamp path, which is 22 % of the flush's p90 wait.
- **Rejected:** the train.sh trap. `pr_exit_trap` already TERMs `merge_train.py` first, and its `finally` blocks release the hold. No trap catches SIGKILL. A possible second-TERM gap in the unwind is the fixer's first probe, not a ruled fact.

The diff is one file against the merge base: `dev/programme/triage/s6-batch131.md`, the ruling. No product behaviour changes.

## Head

`65206847cbd43a422151638bfe6a2a496c5dcb98`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`. `ruling_verdict` reads P402 `ACCEPT`, and a carry citing it passes `triage_refusal`. With the verdict flipped to REJECT, the same carry is refused as "not an ACCEPT ruling (REJECT)". The group brief text in the ruling's `Binding:` also passes `triage_refusal`.

## Null control

P403 reads `None`. With the file absent, a carry citing P402 is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat be813ecd4...65206847cbd43a422151638bfe6a2a496c5dcb98`: 1 file.
- Every ruling figure is printed by the command the ruling names beside it.
- No capped file is touched.

## Red checks

`none`. The merge base is main `be813ecd4`, whose 81 check-runs include no failure. This head's checks run after its push.

## Forward-carry

none

## Friction

none
