Triage batch 196 rules P620 (queue line 298, the CI gate livelock that held #3445 in the train), 2026-11-11. It holds one ruling.

- **P620, ACCEPT: new hotfix group R10-HOTFIX-GATE-REDISPATCH-LOOP** (M, lane C, severity high, opus). It is a merge-blocking livelock, so the bar is the hotfix route.
  - `tools/ci/gate.py:195-223` takes a cancelled run's completed jobs as a unit's source and reads its conclusion (`:232-233`); the orchestrator's cancel of 43022147048 turned 43013039961's re-run gate red.
  - `tools/ci/sweep.py:191-213` counts a dispatch as the fresh judge only if created after the stale gate completed, so re-running an old gate re-dispatches.
  - 10 of 43 `CI code` dispatches (23%) over 11-10..11 started at a head that already had a successful dispatch (#3446 five times at one head); about 8.5 runner-hours at a 51 min median. Null: 26 of 32 heads got one dispatch.

The diff is one file against the merge base: `dev/programme/triage/s6-batch196.md`, the ruling. No product behaviour changes.

## Head

`f71889e1764accb81b0928e62502a39bb1db7ddd`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P620 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P620 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P621 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ee64358be7...f71889e1764accb81b0928e62502a39bb1db7ddd`: 1 file, 74 insertions, 1 commit. `tests/layout.py --guard`: 0 refusals.
- The figures come from one REST read of workflow_dispatch runs (43 `CI code` runs), the orchestrator's unstick log, and `tools/ci/gate.py` and `tools/ci/sweep.py` at `ee64358be7`.

## Red checks

none

## Forward-carry

none

## Friction

none
