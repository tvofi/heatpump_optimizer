Triage batch 201 rules P627 (queue line 305), 2026-11-11. It holds one ruling.

- **P627, ACCEPT narrowed: open_driver backs off on STALE CHECKOUT, an environment refusal.**
  - (a) becomes a new group, R10-FLY-OPENER-STALE-ENV (S, sonnet). A STALE CHECKOUT result is keyed on the tools checkout HEAD: it sets no backoff, does not count toward `MAX_TRIES`, and is retried on the first pass after the HEAD changes. Branch-side failures keep their backoff.
  - The case is measured from the driver log over 29 h. STALE CHECKOUT is 14 of the 22 failures (64%), across 11 topics, with a median of about 17 min to the next result. One topic reached stuck, and one merge-stopping hotfix was delayed 20 min.
  - (b) is an orchestrator-local change to the session beat script's freshness arm: rotate on the first 15-min pass after a staling main merge, not hourly. It needs no roster group.

The diff is one file against the merge base: `dev/programme/triage/s6-batch201.md`, the ruling. No product behaviour changes.

## Head

`51df6039fca185c9a67c6ad98e2b3fc6608d56fa`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P627 as ACCEPT, and a citation of it passes (`None`).
- With P627's verdict text flipped, the citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P628 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 60413046e3...51df6039fca185c9a67c6ad98e2b3fc6608d56fa`: 1 file, 75 insertions, 1 commit. `tests/layout.py --guard`: 0 refusals.
- The figures come from:
  - the roster at `b4a41e1e3b`;
  - the open-driver log's 66 RESULT lines, 2026-11-10T08:50Z-2026-11-11T13:54Z;
  - `git log --first-parent` on origin/main for the last 24 h.

## Red checks

none

## Forward-carry

none

## Friction

none
